import csv
import glob
import os
import statistics
import matplotlib.pyplot as plt
from sudoku import load_puzzle, count_clues, is_solution
from solvers import solve_backtracking, solve_mrv_fc

repeats = 5 # time is the median of this many runs
Run_limit = 20000000    # plain backtracking gives up after this many nodes
Output_dir = "results"

METHODS = [
    ("Backtracking", solve_backtracking),
    ("MRV + FC", solve_mrv_fc),
]
# run a solver on a puzzle multiple times and return the first result and the median time
def run(solver, puzzle):
    times = []
    first = None
    for i in range(repeats):
        res = solver(puzzle, max_nodes=Run_limit)
        times.append(res.seconds)
        if first is None:
            first = res
        if res.status == "gave up" or res.seconds > 5:
            break  
    return first, statistics.median(times)

def main():
    #load all the puzzles in the puzzles directory and run each solver on each puzzle
    files = sorted(glob.glob("puzzles/*.txt"))
    os.makedirs(Output_dir, exist_ok=True)
    rows = []

    print(f"{'puzzle':28} {'clues':>5}  {'method':13} {'status':12} {'time (s)':>10} {'nodes':>10} {'backtracks':>11}")
    for path in files:
        try:
            # load the puzzle from the given file
            puzzle = load_puzzle(path)
        except ValueError as e:
            print(f"skipping {path}: {e}")
            continue
        name = os.path.splitext(os.path.basename(path))[0]
        # choose the solver based on the method name and run it on the puzzle
        for method, solver in METHODS:
            res, t = run(solver, puzzle)
            if res.status == "solved":
                assert is_solution(res.solution, puzzle), f"wrong answer for {name}"
            print(f"{name:28} {count_clues(puzzle):5}  {method:13} {res.status:12} {t:10.4f} {res.nodes:10} {res.backtracks:11}")
            rows.append({"puzzle": name, "clues": count_clues(puzzle), "method": method,
                         "status": res.status, "time_s": round(t, 6),
                         "nodes": res.nodes, "backtracks": res.backtracks})

    # save the results to a CSV file and make charts
    csv_path = os.path.join(Output_dir, "results.csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print("\nsaved", csv_path)
    # make charts for time, nodes, and backtracks
    make_charts(rows)

def make_charts(rows):
    # one chart per measurement, with a pair of bars (one per method) for each puzzle
    puzzles = []
    for r in rows:
        if r["puzzle"] not in puzzles:
            puzzles.append(r["puzzle"])

    for key, title in [("time_s", "time"), ("nodes", "nodes"), ("backtracks", "backtracks")]:
        plt.figure(figsize=(10, 5))
        width = 0.4
        for i, (method, _) in enumerate(METHODS):
            values = []
            for p in puzzles:
                for r in rows:
                    if r["puzzle"] == p and r["method"] == method:
                        # log scale can't show 0, so use a tiny value instead
                        values.append(max(r[key], 0.1))
            x = [j + i * width for j in range(len(puzzles))]
            plt.bar(x, values, width, label=method)

        plt.yscale("log")
        plt.xticks([j + width / 2 for j in range(len(puzzles))], puzzles, rotation=45, ha="right")
        plt.ylabel(title)
        plt.title(f"{title} per puzzle")
        plt.legend()
        plt.tight_layout()
        out = os.path.join(Output_dir, f"{title}.png")
        plt.savefig(out)
        plt.close()
        print("saved", out)


if __name__ == "__main__":
    main()
