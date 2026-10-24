import argparse
import sys

from sudoku import load_puzzle, format_grid, count_clues
from solvers import SOLVERS


def main():
    parser = argparse.ArgumentParser(description="Solve a 9x9 Sudoku read from a txt file")
    parser.add_argument("file")
    parser.add_argument("-s", "--solver", choices=list(SOLVERS), default="mrv")
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    try:
        # load the puzzle from the given file
        puzzle = load_puzzle(args.file)
    except (ValueError, OSError) as e:
        print(f"Could not read {args.file}: {e}")
        sys.exit(1)

    print(f"Puzzle ({count_clues(puzzle)} clues):")
    print(format_grid(puzzle))

    # get solver and solve the puzzle
    result = SOLVERS[args.solver](puzzle, max_nodes=args.limit)

    print()
    if result.status == "solved":
        print("Solution:")
        print(format_grid(result.solution))
    elif result.status == "gave up":
        print("Search limit reached with no solution (" + result.message + ") ")
    else:
        print("No solution found")
        if result.message:
            print("Reason: " + result.message)

    print()
    print(f"Method:{result.method}")
    print(f"Time: {result.seconds:.4f} seconds")
    print(f"Nodes:{result.nodes}")
    print(f"Backtracks: {result.backtracks}")

if __name__ == "__main__":
    main()
