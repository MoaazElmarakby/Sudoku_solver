import time
from sudoku import CELLS, PEERS, find_clash

class Result:
    def __init__(self, method):
        self.method = method
        self.status = ""
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
    # backtracking search, trying the digits 1 to 9 in order for each empty cell.
    res = Result("Backtracking")
    grid = [row[:] for row in puzzle]

    #check if there is a clash in the initial puzzle
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
            # no solution found, backtrack
            grid[r][c] = 0
            res.backtracks += 1
        return False

    start = time.perf_counter()
    try:
        found = search(0)
        res.status = "solved" if found else "no solution"
    except _LimitReached:
        # limit reached, give up and return the partial solution
        found = False
        res.status = "gave up"
        res.message = f"stopped after {max_nodes} nodes"
    res.seconds = time.perf_counter() - start

    if found:
        res.solution = grid
    return res


def solve_mrv_fc(puzzle, max_nodes=None):
    # backtracking search with MRV + forward checking
    res = Result("MRV + forward checking")
    grid = [row[:] for row in puzzle]

    clash = find_clash(grid)
    # check if there is a clash in the initial puzzle
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
        # pick the empty cell with the fewest remaining values (MRV)
        best = None
        for (r, c) in CELLS:
            if grid[r][c] == 0:
                if best is None or len(domains[(r, c)]) < len(domains[best]):
                    best = (r, c)
                    if len(domains[best]) <= 1:
                        break   # nothing can be better than 1, so stop searching
        return best

    def assign(cell, d):
        # assign digit d to cell, and remove d from the domains of its peers
        r, c = cell
        grid[r][c] = d
        removed = []
        for p in PEERS[cell]:
            if grid[p[0]][p[1]] == 0 and d in domains[p]:
                domains[p].remove(d)
                removed.append(p)
                if not domains[p]:
                    return removed, False   # no values left for a peer
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
            found = False   # empty cell with no possible values, so no solution
        else:
            found = search()
        res.status = "solved" if found else "no solution"
    except _LimitReached:

        # limit reached, give up and return the partial solution
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
