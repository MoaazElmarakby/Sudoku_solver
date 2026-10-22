# Two search-based solvers that share the same CSP model (see sudoku.py):
#
#   solve_backtracking - plain chronological backtracking, cells filled left to
#                        right, top to bottom. Used as the baseline.
#   solve_mrv_fc       - backtracking + MRV variable ordering + forward checking.
#                        This is the main solver.
#
# Both count the same things so the results can be compared directly:
#   nodes      - number of times a digit was placed in a cell
#   backtracks - number of times a placed digit had to be taken out again
#   seconds    - wall-clock time of the search (time.perf_counter)

import time

from sudoku import CELLS, PEERS, find_clash


class Result:
    def __init__(self, method):
        self.method = method
        self.status = ""        # "solved", "no solution" or "gave up"
        self.solution = None
        self.nodes = 0
        self.backtracks = 0
        self.seconds = 0.0
        self.message = ""

    def summary(self):
        return (f"{self.method}: {self.status} in {self.seconds:.4f} s, "
                f"{self.nodes} nodes, {self.backtracks} backtracks")


class _LimitReached(Exception):
    pass


def solve_backtracking(puzzle, max_nodes=None):
    """Plain backtracking: fill the empty cells in a fixed order, checking each
    digit against the cells already filled."""
    res = Result("Backtracking")
    grid = [row[:] for row in puzzle]

    clash = find_clash(grid)
    if clash:
        res.status = "no solution"
        res.message = "the given digits break the rules: " + clash
        return res

    empty = [(r, c) for r, c in CELLS if grid[r][c] == 0]

    def consistent(r, c, d):
        for pr, pc in PEERS[(r, c)]:
            if grid[pr][pc] == d:
                return False
        return True

    def search(i):
        if i == len(empty):
            return True
        r, c = empty[i]
        for d in range(1, 10):
            if not consistent(r, c, d):
                continue
            if max_nodes and res.nodes >= max_nodes:
                raise _LimitReached()
            res.nodes += 1
            grid[r][c] = d
            if search(i + 1):
                return True
            # dead end further down, undo and try the next digit
            grid[r][c] = 0
            res.backtracks += 1
        return False

    start = time.perf_counter()
    try:
        found = search(0)
        res.status = "solved" if found else "no solution"
    except _LimitReached:
        found = False
        res.status = "gave up"
        res.message = f"stopped after {max_nodes} nodes"
    res.seconds = time.perf_counter() - start

    if found:
        res.solution = grid
    return res


def solve_mrv_fc(puzzle, max_nodes=None):
    """Backtracking with MRV (pick the empty cell with the fewest values left)
    and forward checking (after placing d, remove d from the domains of the
    empty peers and backtrack straight away if one of them becomes empty)."""
    res = Result("MRV + forward checking")
    grid = [row[:] for row in puzzle]

    clash = find_clash(grid)
    if clash:
        res.status = "no solution"
        res.message = "the given digits break the rules: " + clash
        return res

    start = time.perf_counter()

    # initial domains: 1-9 minus whatever the peers already hold
    domains = {}
    for cell in CELLS:
        r, c = cell
        if grid[r][c]:
            domains[cell] = {grid[r][c]}
        else:
            used = {grid[pr][pc] for pr, pc in PEERS[cell]}
            domains[cell] = set(range(1, 10)) - used

    def pick_cell():
        # MRV - the empty cell with the smallest domain (first one wins ties)
        best = None
        for (r, c) in CELLS:
            if grid[r][c] == 0:
                if best is None or len(domains[(r, c)]) < len(domains[best]):
                    best = (r, c)
                    if len(domains[best]) <= 1:
                        break   # can't do better than this
        return best

    def assign(cell, d):
        # place d and prune it from the empty peers; remember what was removed
        r, c = cell
        grid[r][c] = d
        removed = []
        for p in PEERS[cell]:
            if grid[p[0]][p[1]] == 0 and d in domains[p]:
                domains[p].remove(d)
                removed.append(p)
                if not domains[p]:
                    return removed, False   # a peer has no values left
        return removed, True

    def unassign(cell, d, removed):
        grid[cell[0]][cell[1]] = 0
        for p in removed:
            domains[p].add(d)

    def search():
        cell = pick_cell()
        if cell is None:
            return True   # no empty cells left
        for d in sorted(domains[cell]):
            if max_nodes and res.nodes >= max_nodes:
                raise _LimitReached()
            res.nodes += 1
            removed, ok = assign(cell, d)
            if ok and search():
                return True
            unassign(cell, d, removed)
            res.backtracks += 1
        return False

    try:
        if any(not domains[(r, c)] for r, c in CELLS if grid[r][c] == 0):
            found = False   # some empty cell has no possible digit at all
        else:
            found = search()
        res.status = "solved" if found else "no solution"
    except _LimitReached:
        found = False
        res.status = "gave up"
        res.message = f"stopped after {max_nodes} nodes"
    res.seconds = time.perf_counter() - start

    if found:
        res.solution = grid
    return res


SOLVERS = {
    "mrv": solve_mrv_fc,
    "backtracking": solve_backtracking,
}
