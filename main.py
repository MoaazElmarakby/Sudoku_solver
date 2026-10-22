# Command line version.
#
#   python main.py puzzles/01_easy.txt
#   python main.py puzzles/04_hard.txt --solver backtracking

import argparse
import sys

from sudoku import load_puzzle, format_grid, count_clues
from solvers import SOLVERS


def main():
    parser = argparse.ArgumentParser(description="Solve a 9x9 Sudoku read from a .txt file")
    parser.add_argument("file", help="puzzle file (9 rows of 9 digits, 0 = empty)")
    parser.add_argument("-s", "--solver", choices=list(SOLVERS), default="mrv",
                        help="search method (default: mrv = MRV + forward checking)")
    parser.add_argument("--limit", type=int, default=None,
                        help="give up after this many nodes (useful for plain backtracking)")
    args = parser.parse_args()

    try:
        puzzle = load_puzzle(args.file)
    except (ValueError, OSError) as e:
        print(f"Could not read {args.file}: {e}")
        sys.exit(1)

    print(f"Puzzle ({count_clues(puzzle)} clues):")
    print(format_grid(puzzle))

    result = SOLVERS[args.solver](puzzle, max_nodes=args.limit)

    print()
    if result.status == "solved":
        print("Solution:")
        print(format_grid(result.solution))
    elif result.status == "gave up":
        print("Search limit reached before a solution was found (" + result.message + ").")
    else:
        print("This puzzle has no solution.")
        if result.message:
            print("Reason: " + result.message)

    print()
    print(f"Method: {result.method}")
    print(f"Time:   {result.seconds:.4f} s")
    print(f"Nodes:  {result.nodes}")
    print(f"Backtracks: {result.backtracks}")


if __name__ == "__main__":
    main()
