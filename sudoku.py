# Basic Sudoku helpers: the CSP model, reading puzzle files and printing grids.
#
# CSP view of the puzzle:
#   variables   - the 81 cells, stored as (row, col) with 0-based indices
#   domains     - {1..9} for an empty cell, {d} for a cell given as d
#   constraints - every cell must be different from its 20 peers
#                 (the other cells in its row, column and 3x3 box)

import os


class PuzzleError(Exception):
    """Raised when a puzzle file can't be read or has the wrong format."""


CELLS = [(r, c) for r in range(9) for c in range(9)]

rows = [[(r, c) for c in range(9)] for r in range(9)]
cols = [[(r, c) for r in range(9)] for c in range(9)]
boxes = [[(br + i, bc + j) for i in range(3) for j in range(3)]
         for br in (0, 3, 6) for bc in (0, 3, 6)]
units = rows + cols + boxes 

def find_peers(r, c):
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
    """Read a 9x9 grid from a .txt file (values separated by spaces).
    Empty cells are written as 0. Returns a list of 9 lists of ints."""
    ext = os.path.splitext(path)[1].lower()
    if ext != ".txt":
        raise PuzzleError(f"unsupported file type '{ext}', use .txt")
    with open(path) as f:
        return parse_puzzle(f.read())


def parse_puzzle(text):
    """Same as load_puzzle but works on the file's text (used for uploaded files)."""
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    if len(lines) != 9:
        raise PuzzleError(f"expected 9 rows but found {len(lines)}")

    grid = []
    for row_no, line in enumerate(lines, start=1):
        values = [v.strip() for v in line.split()]
        if len(values) != 9:
            raise PuzzleError(f"row {row_no} has {len(values)} values, expected 9")
        row = []
        for v in values:
            if len(v) != 1 or not v.isdigit():
                raise PuzzleError(f"row {row_no} has an invalid value '{v}'")
            row.append(int(v))
        grid.append(row)
    return grid


def find_clash(grid):
    """If two given digits already break a rule, describe the clash. Otherwise None."""
    for (r, c) in CELLS:
        d = grid[r][c]
        if d == 0:
            continue
        for (pr, pc) in PEERS[(r, c)]:
            if grid[pr][pc] == d:
                return f"{d} appears twice (row {r+1} col {c+1} and row {pr+1} col {pc+1})"
    return None


def is_solution(grid, puzzle=None):
    """True if grid is a complete valid Sudoku (and keeps the clues of puzzle, if given)."""
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
