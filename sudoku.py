import os
CELLS = [(r, c) for r in range(9) for c in range(9)]

rows = [[(r, c) for c in range(9)] for r in range(9)]
cols = [[(r, c) for r in range(9)] for c in range(9)]
boxes = [[(br + i, bc + j) for i in range(3) for j in range(3)]
         for br in (0, 3, 6) for bc in (0, 3, 6)]
UNITS = rows + cols + boxes 

def find_peers(r, c):
    """return a sorted list of the 20 peers of cell (r, c)"""
    peers = set()
    for i in range(9):
        peers.add((r, i))
        peers.add((i, c))
    br = 3 * (r // 3)
    bc = 3 * (c // 3)
    for i in range(br, br + 3):
        for j in range(bc, bc + 3):
            peers.add((i, j))
    peers.remove((r, c))
    return sorted(peers)

PEERS = {cell: find_peers(*cell) for cell in CELLS}

def load_puzzle(path):
    """
        Read puzzle from a txt file.
        Empty cells are written as 0. Returns a list of 9 lists of ints.
    """
    ext = os.path.splitext(path)[1].lower()
    if ext != ".txt":
        raise ValueError(f"unsupported file type '{ext}', use .txt")
    with open(path) as f:
        return parse_puzzle(f.read())

def parse_puzzle(text):
    """load a puzzle and create a 9x9 grid of ints (0 = empty)"""
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    if len(lines) != 9:
        raise ValueError(f"expected 9 rows but found {len(lines)}")

    grid = []
    for row_no, line in enumerate(lines, start=1):
        values = [v.strip() for v in line.split()]
        if len(values) != 9:
            raise ValueError(f"row {row_no} has {len(values)} values, expected 9")
        row = []
        for v in values:
            if len(v) != 1 or not v.isdigit():
                raise ValueError(f"row {row_no} has an invalid value '{v}'")
            row.append(int(v))
        grid.append(row)
    return grid

def find_clash(grid):
    """check if the grid has any clashes (two of the same digit in a row, column, or box)"""
    for (r, c) in CELLS:
        d = grid[r][c]
        if d == 0:
            continue
        for (pr, pc) in PEERS[(r, c)]:
            if grid[pr][pc] == d:
                return f"{d} appears twice (row {r+1} col {c+1} and row {pr+1} col {pc+1})"
    return None

def is_solution(grid, puzzle=None):
    """check if grid is a complete valid Sudoku."""
    for unit in UNITS:
        if sorted(grid[r][c] for r, c in unit) != list(range(1, 10)):
            return False
    if puzzle is not None:
        for r, c in CELLS:
            if puzzle[r][c] and puzzle[r][c] != grid[r][c]:
                return False
    return True

def format_grid(grid):
    line = "+-------+-------+-------+"
    out = [line]
    for r in range(9):
        text = "|"
        for c in range(9):
            d = grid[r][c]
            text += " " + (str(d) if d else ".")
            if c % 3 == 2:
                text += " |"
        out.append(text)
        if r % 3 == 2:
            out.append(line)
    return "\n".join(out)

def count_clues(grid):
    return sum(1 for r, c in CELLS if grid[r][c])
