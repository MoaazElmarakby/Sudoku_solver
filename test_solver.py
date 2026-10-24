import unittest
from sudoku import load_puzzle, is_solution
from solvers import solve_backtracking, solve_mrv_fc
Puzzles = [
    "puzzles/01_easy.txt",
    "puzzles/02_easy.txt",
    "puzzles/03_medium.txt",
    "puzzles/04_hard.txt",
    "puzzles/06_extreme_inkala.txt",
]
class TestSudokuSolver(unittest.TestCase):
    # test that the solvers can solve a few puzzles and that the solutions are valid
    def test_load_puzzle(self):
        puzzle = load_puzzle(Puzzles[0])
        self.assertEqual(len(puzzle), 9)
        self.assertTrue(all(len(row) == 9 for row in puzzle))

    def test_mrv_fc(self):
        for path in Puzzles:
            puzzle = load_puzzle(path)
            result = solve_mrv_fc(puzzle)
            self.assertEqual(result.status, "solved", path)
            self.assertTrue(is_solution(result.solution, puzzle), path)

    def test_backtracking(self):
        for path in Puzzles[:3]:
            puzzle = load_puzzle(path)
            result = solve_backtracking(puzzle)
            self.assertEqual(result.status, "solved", path)
            self.assertTrue(is_solution(result.solution, puzzle), path)

    def test_invalid_puzzle(self):
        with self.assertRaises(ValueError):
            load_puzzle("puzzles/invalid/only_8_rows.txt")


if __name__ == "__main__":
    unittest.main()
