# Sudoku Solver

This a project to solve 9x9 sudoku puzzles using backtracking methods. There are 2 different algorithms
basic backtracking and backtracking with MRV + forward checking. It includes evaluation for each algorithm and comparison between them. In addition to that UI application.

## Requirements

Python 3.9 or later is required.
Streamlit is required to the GUI.

```bash
pip install -r requirements.txt
```


## Files

| File | Description |
|---|---|
| `sudoku.py` | Reads puzzle files, check the puzzle valid or not and prints them |
| `solvers.py` | Implements the solvers algorithms |
| `main.py` | Runs the pipeline, loads the files and solve the puzzles |
| `app.py` | Implements the GUI using Streamlit|
| `benchmark.py` | Tests both methods and saves the results |
| `test_solver.py` | Implements the unit tests |
| `puzzles/` | Directory contains test puzzles. The txt puzzel files are generated using AI tool |

## How to Run

Run the solver on a puzzle:
```bash
python main.py puzzles/06_extreme_inkala.txt
```

Use basic backtracking:
```bash
python main.py puzzles/04_hard.txt --solver backtracking
```

Start the web interface:
```bash
streamlit run app.py
```

Run the benchmark:
```bash
python benchmark.py
```

Run the unit tests:
```bash
python -m unittest test_solver -v
```

The web interface opens at [http://localhost:8501](http://localhost:8501). 
Upload a puzzle
select a solving method, and click **Solve**.


## Performance Metrics

The benchmark measures three things:

- **Nodes:** Number of times the solver tries finding a number in each cell.
- **Backtracks:** Number of times the solver removes a number because it leads to a invalid solution.
- **Time:** How long the solver takes to finish.

## References :

[Solving Every Sudoku Puzzle](https://www.norvig.com/sudoku.html)