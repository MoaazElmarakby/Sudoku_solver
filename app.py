
import pandas as pd
import streamlit as st

from sudoku import parse_puzzle, count_clues, find_clash, PuzzleError
from solvers import solve_mrv_fc, solve_backtracking

METHODS = {
    "MRV + forward checking": solve_mrv_fc,
    "Plain backtracking": solve_backtracking,
}
NODE_LIMIT = 2000000   # stops plain backtracking from running for ages

BOARD_CSS = """
<style>
table.sudoku { border-collapse: collapse; margin: 4px 0 12px 0; border: 3px solid #222; }
table.sudoku td { width: 40px; height: 40px; text-align: center; font-size: 21px;
                  border: 1px solid #b5b5b5; background: #fff; padding: 0; }
table.sudoku td.clue { font-weight: 700; color: #111; }
table.sudoku td.solved { color: #1d5fbf; }
table.sudoku td.right { border-right: 3px solid #222; }
table.sudoku td.bottom { border-bottom: 3px solid #222; }
</style>
"""

def board_html(puzzle, solution=None):
    rows = []
    for r in range(9):
        cells = []
        for c in range(9):
            classes = []
            if puzzle[r][c]:
                digit = puzzle[r][c]
                classes.append("clue")
            elif solution:
                digit = solution[r][c]
                classes.append("solved")
            else:
                digit = ""
            if c in (2, 5):
                classes.append("right")
            if r in (2, 5):
                classes.append("bottom")
            cells.append(f'<td class="{" ".join(classes)}">{digit}</td>')
        rows.append("<tr>" + "".join(cells) + "</tr>")
    return BOARD_CSS + '<table class="sudoku">' + "".join(rows) + "</table>"


def set_puzzle(grid, name=None, error=None):
    st.session_state.puzzle = grid
    st.session_state.name = name
    st.session_state.load_error = error
    st.session_state.result = None
    st.session_state.comparison = None


st.set_page_config(page_title="Sudoku Solver", layout="wide")

if "puzzle" not in st.session_state:
    st.session_state.file_id = None
    set_puzzle(None)

st.title("Sudoku Solver")

# split window into two columns, left for input, right for output
left, right = st.columns(2, gap="large")


# input column
with left:
    st.subheader("Puzzle")
    uploaded = st.file_uploader("Open a puzzle file (.txt, 0 = empty cell)",type=["txt"])

    if uploaded is None:
        if st.session_state.file_id is not None:   # the file was removed
            st.session_state.file_id = None
            set_puzzle(None)
    elif uploaded.file_id != st.session_state.file_id:
        st.session_state.file_id = uploaded.file_id
        try:
            set_puzzle(parse_puzzle(uploaded.getvalue().decode("utf-8")), uploaded.name)
        except (PuzzleError, UnicodeDecodeError) as e:
            set_puzzle(None, error=f"Could not read {uploaded.name}: {e}")

    puzzle = st.session_state.puzzle
    if st.session_state.load_error:
        st.error(st.session_state.load_error)

    if puzzle is not None:
        st.markdown(board_html(puzzle), unsafe_allow_html=True)
        st.write(f"**{st.session_state.name}**, {count_clues(puzzle)} clues")
        # clash = find_clash(puzzle)
        # if clash:
        #     st.warning("The clues break the rules: " + clash)

    method = st.radio("Method", list(METHODS), horizontal=True)
    b1, b2 = st.columns(2)
    solve_clicked = b1.button("Solve", type="primary", use_container_width=True, disabled=puzzle is None)
    compare_clicked = b2.button("Compare both methods", use_container_width=True, disabled=puzzle is None)

if solve_clicked:
    with st.spinner(f"Solving with {method}..."):
        st.session_state.result = METHODS[method](puzzle, max_nodes=NODE_LIMIT)

if compare_clicked:
    rows = []
    with st.spinner("Running both methods..."):
        for name, solver in METHODS.items():
            res = solver(puzzle, max_nodes=NODE_LIMIT)
            rows.append({"Method": name, "Result": res.status,
                         "Time (s)": round(res.seconds, 4),
                         "Nodes": res.nodes, "Backtracks": res.backtracks})
    st.session_state.comparison = rows



# output column
with right:
    st.subheader("Solution")
    res = st.session_state.result

    if puzzle is None:
        st.info("Upload a puzzle file to start.")
    elif res is None:
        st.info("Press **Solve** to fill in the empty cells.")
    else:
        if res.status == "solved":
            st.markdown(board_html(puzzle, res.solution), unsafe_allow_html=True)
            st.success(f"Solved with {res.method}.")
        elif res.status == "gave up":
            st.warning(f"Gave up after {NODE_LIMIT:,} nodes. Try MRV + forward checking instead.")
        else:
            st.error("This puzzle has no solution." + (f" Reason: {res.message}." if res.message else ""))

        m1, m2, m3 = st.columns(3)
        m1.metric("Time", f"{res.seconds:.4f} s")
        m2.metric("Nodes", f"{res.nodes:,}")
        m3.metric("Backtracks", f"{res.backtracks:,}")

    if puzzle is not None and st.session_state.comparison:
        st.subheader("Comparison")
        st.dataframe(pd.DataFrame(st.session_state.comparison), hide_index=True, use_container_width=True)
