# Runs both solvers on every puzzle in puzzles/ and records time, nodes and
# backtracks. Results go to results/results.csv, plus a few bar charts if
# matplotlib is installed.
#
#   python benchmark.py

import csv
import glob
import os
import statistics

from sudoku import load_puzzle, count_clues, is_solution, PuzzleError
from solvers import solve_backtracking, solve_mrv_fc

REPEATS = 5                   # time is the median of this many runs
BACKTRACKING_LIMIT = 20000000  # plain backtracking gives up after this many nodes
OUT_DIR = "results"

METHODS = [
    ("Backtracking", solve_backtracking),
    ("MRV + FC", solve_mrv_fc),
]


def run(solver, puzzle):
    times = []
    first = None
    for i in range(REPEATS):
        res = solver(puzzle, max_nodes=BACKTRACKING_LIMIT)
        times.append(res.seconds)
        if first is None:
            first = res
        if res.status == "gave up" or res.seconds > 5:
            break   # long runs are only done once, the noise is small anyway
    # nodes and backtracks are the same on every run, only time varies
    return first, statistics.median(times)


def main():
    files = sorted(glob.glob("puzzles/*.txt"))
    os.makedirs(OUT_DIR, exist_ok=True)
    rows = []

    print(f"{'puzzle':28} {'clues':>5}  {'method':13} {'status':12} {'time (s)':>10} {'nodes':>10} {'backtracks':>11}")
    for path in files:
        try:
            puzzle = load_puzzle(path)
        except PuzzleError as e:
            print(f"skipping {path}: {e}")
            continue
        name = os.path.splitext(os.path.basename(path))[0]
        for method, solver in METHODS:
            res, t = run(solver, puzzle)
            if res.status == "solved":
                assert is_solution(res.solution, puzzle), f"wrong answer for {name}"
            print(f"{name:28} {count_clues(puzzle):5}  {method:13} {res.status:12} {t:10.4f} {res.nodes:10} {res.backtracks:11}")
            rows.append({"puzzle": name, "clues": count_clues(puzzle), "method": method,
                         "status": res.status, "time_s": round(t, 6),
                         "nodes": res.nodes, "backtracks": res.backtracks})

    csv_path = os.path.join(OUT_DIR, "results.csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print("\nsaved", csv_path)

    try:
        make_charts(rows)
    except ImportError:
        print("matplotlib not installed, skipping charts")


def make_charts(rows):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    puzzles = []
    for r in rows:
        if r["puzzle"] not in puzzles:
            puzzles.append(r["puzzle"])
    colours = {"Backtracking": "#eb6834", "MRV + FC": "#2a78d6"}

    for key, label in [("time_s", "Time (seconds)"), ("nodes", "Nodes (digits placed)"),
                       ("backtracks", "Backtracks")]:
        fig, ax = plt.subplots(figsize=(9, 4.5))
        width = 0.38
        for i, (method, _) in enumerate(METHODS):
            values, stopped = [], []
            for p in puzzles:
                r = next(x for x in rows if x["puzzle"] == p and x["method"] == method)
                values.append(max(r[key], 1e-5 if key == "time_s" else 0.8))  # log scale can't show 0
                stopped.append(r["status"] == "gave up")
            xs = [j + (i - 0.5) * width for j in range(len(puzzles))]
            bars = ax.bar(xs, values, width - 0.03, label=method, color=colours[method])
            for bar, s in zip(bars, stopped):
                if s:
                    bar.set_hatch("//")
                    ax.annotate("limit hit", (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                                ha="center", va="bottom", fontsize=8, color="#444444")
        ax.set_yscale("log")
        ax.set_ylabel(label + ", log scale")
        ax.set_xticks(range(len(puzzles)))
        ax.set_xticklabels([p.replace("_", " ", 1).replace("_", "\n") for p in puzzles], fontsize=8)
        ax.grid(axis="y", color="#dddddd", linewidth=0.6)
        ax.set_axisbelow(True)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        ax.legend(frameon=False)
        ax.set_title(f"{label.split(' (')[0]} per puzzle: plain backtracking vs MRV + forward checking", fontsize=11)
        fig.tight_layout()
        out = os.path.join(OUT_DIR, f"{key.replace('_s', '')}.png")
        fig.savefig(out, dpi=150)
        plt.close(fig)
        print("saved", out)


if __name__ == "__main__":
    main()
