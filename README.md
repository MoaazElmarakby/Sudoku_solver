# Sudoku Solver

Solves 9x9 Sudoku puzzles using backtracking search with the MRV heuristic and
forward checking. Plain backtracking is included as a baseline for comparison.

Needs Python 3.9+. The web interface uses Streamlit, and the charts in
`benchmark.py` use matplotlib:

```
pip install -r requirements.txt
```

The solvers and the command line program need nothing beyond the standard library.

## Files

| File | What it does |
|---|---|
| `sudoku.py` | CSP model (cells, peers), reading `.txt` files, checking and printing grids |
| `solvers.py` | `solve_backtracking` (baseline) and `solve_mrv_fc` (main solver) |
| `main.py` | command line program |
| `app.py` | web interface (Streamlit) |
| `benchmark.py` | runs both solvers on every puzzle, writes `results/` |
| `test_solver.py` | unit tests |
| `puzzles/` | test puzzles; `puzzles/invalid/` has broken files for testing errors |

## Running it

```
python main.py puzzles/06_extreme_inkala.txt
python main.py puzzles/04_hard.txt --solver backtracking
streamlit run app.py
python benchmark.py
python -m unittest test_solver -v
```

`streamlit run app.py` opens the interface in your browser (http://localhost:8501).
Upload a puzzle file, choose a method and press Solve.
"Compare both methods" runs both solvers on the same puzzle.

## Puzzle format

9 lines, 9 values per line, separated by spaces.
Use 0 for an empty cell.

```
0 0 3 0 2 0 6 0 0
9 0 0 3 0 5 0 0 1
...
```

## Metrics

- **nodes**: number of times a digit was placed in a cell
- **backtracks**: number of times a placed digit had to be removed again
- **time**: `time.perf_counter()` around the search, median of 5 runs in the benchmark
