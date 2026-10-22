# Correctness tests. Run with:  python -m unittest test_solver -v

import glob
import unittest

from sudoku import load_puzzle, parse_puzzle, is_solution
from solvers import solve_backtracking, solve_mrv_fc

SOLVABLE = [
    "puzzles/01_easy.txt",
    "puzzles/02_easy.txt",
    "puzzles/03_medium.txt",
    "puzzles/04_hard.txt",
    "puzzles/05_hard_17_clues.txt",
    "puzzles/06_extreme_inkala.txt",
    "puzzles/07_anti_backtracking.txt",
    "puzzles/09_empty_grid.txt",
]

# plain backtracking needs far too long on these, so it is only tested on the rest
SLOW_FOR_BACKTRACKING = {"puzzles/05_hard_17_clues.txt", "puzzles/07_anti_backtracking.txt"}


class TestReading(unittest.TestCase):

    def test_reads_txt(self):
        for path in glob.glob("puzzles/*.txt"):
            grid = load_puzzle(path)
            self.assertEqual(len(grid), 9)
            self.assertTrue(all(len(row) == 9 for row in grid))

    def test_bad_files_are_rejected(self):
        for path in ["puzzles/invalid/only_8_rows.txt",
                     "puzzles/invalid/letter_in_grid.txt",
                     "puzzles/invalid/wrong_extension.dat"]:
            with self.assertRaises(ValueError):
                load_puzzle(path)


    def test_parse_text_matches_file(self):
        # the web app reads uploaded files from text, this must give the same grid
        with open("puzzles/02_easy.txt") as f:
            self.assertEqual(parse_puzzle(f.read()), load_puzzle("puzzles/02_easy.txt"))


class TestSolvers(unittest.TestCase):

    def check_solved(self, solver, path):
        puzzle = load_puzzle(path)
        res = solver(puzzle)
        self.assertEqual(res.status, "solved", path)
        self.assertTrue(is_solution(res.solution, puzzle), path)
        return res.solution

    def test_mrv_fc_solves_everything(self):
        for path in SOLVABLE:
            self.check_solved(solve_mrv_fc, path)

    def test_backtracking_solves_the_rest(self):
        for path in SOLVABLE:
            if path not in SLOW_FOR_BACKTRACKING:
                self.check_solved(solve_backtracking, path)

    def test_both_find_the_same_solution(self):
        # these puzzles have exactly one solution, so the answers must match
        for path in SOLVABLE[:6]:
            if path in SLOW_FOR_BACKTRACKING:
                continue
            a = self.check_solved(solve_mrv_fc, path)
            b = self.check_solved(solve_backtracking, path)
            self.assertEqual(a, b, path)

    def test_puzzle_is_not_changed(self):
        puzzle = load_puzzle("puzzles/01_easy.txt")
        before = [row[:] for row in puzzle]
        solve_mrv_fc(puzzle)
        solve_backtracking(puzzle)
        self.assertEqual(puzzle, before)

    def test_unsolvable_puzzle(self):
        puzzle = load_puzzle("puzzles/08_unsolvable.txt")
        for solver in (solve_mrv_fc, solve_backtracking):
            res = solver(puzzle)
            self.assertEqual(res.status, "no solution")
            self.assertIsNone(res.solution)

    def test_clashing_clues(self):
        puzzle = load_puzzle("puzzles/invalid/repeated_digit.txt")
        for solver in (solve_mrv_fc, solve_backtracking):
            res = solver(puzzle)
            self.assertEqual(res.status, "no solution")
            self.assertEqual(res.nodes, 0)

    def test_node_limit(self):
        puzzle = load_puzzle("puzzles/07_anti_backtracking.txt")
        res = solve_backtracking(puzzle, max_nodes=10000)
        self.assertEqual(res.status, "gave up")
        self.assertEqual(res.nodes, 10000)

    def test_already_solved_grid(self):
        solution = solve_mrv_fc(load_puzzle("puzzles/01_easy.txt")).solution
        res = solve_mrv_fc(solution)
        self.assertEqual(res.status, "solved")
        self.assertEqual(res.nodes, 0)


if __name__ == "__main__":
    unittest.main()
