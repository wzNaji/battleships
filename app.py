import streamlit as st
import numpy as np

grid_size = 5
ship_lengths = [3, 2]

if "player_board" not in st.session_state:
    st.session_state.player_board = np.zeros((grid_size, grid_size), dtype=int)
    st.session_state.opponent_board = np.zeros((grid_size, grid_size), dtype=int)
    st.session_state.player_ships = []  # list of confirmed ships
    st.session_state.opponent_ships = []
    st.session_state.current_ship_cells = []  # temp list for selecting current ship
    st.session_state.current_ship_index = 0
    st.session_state.phase = "placing"
    st.session_state.message = f"Double-click {ship_lengths[0]} cells on your board to place your first ship."
    st.session_state.error = ""

st.title("Battleships!")
st.write(st.session_state.message)
if st.session_state.error:
    st.error(st.session_state.error)

def is_valid_ship_selection(cells):
    if len(cells) < 2:
        return True
    rows = [r for r, _ in cells]
    cols = [c for _, c in cells]
    same_row = all(r == rows[0] for r in rows)
    same_col = all(c == cols[0] for c in cols)

    if not (same_row or same_col):
        return False

    if same_row:
        return sorted(cols) == list(range(min(cols), max(cols) + 1))
    if same_col:
        return sorted(rows) == list(range(min(rows), max(rows) + 1))

    return False

# Player board placement phase
def handle_player_grid():
    for row in range(grid_size):
        cols = st.columns(grid_size)
        for col in range(grid_size):
            key = f"cell_{row}_{col}"
            if st.session_state.player_board[row, col] == 1:
                label = "🚢"
            elif (row, col) in st.session_state.current_ship_cells:
                label = "✅"
            else:
                label = " "

            if cols[col].button(label, key=key):
                if st.session_state.phase == "placing":
                    if (row, col) in st.session_state.current_ship_cells:
                        return
                    st.session_state.current_ship_cells.append((row, col))

                    required_length = ship_lengths[st.session_state.current_ship_index]

                    if len(st.session_state.current_ship_cells) == required_length:
                        if is_valid_ship_selection(st.session_state.current_ship_cells):
                            for r, c in st.session_state.current_ship_cells:
                                st.session_state.player_board[r, c] = 1
                            st.session_state.player_ships.append(st.session_state.current_ship_cells)
                            st.session_state.current_ship_cells = []
                            st.session_state.current_ship_index += 1
                            st.session_state.error = ""

                            if st.session_state.current_ship_index == len(ship_lengths):
                                st.session_state.phase = "ready"
                                st.session_state.message = "✅ All ships placed! Ready to play!"
                            else:
                                next_len = ship_lengths[st.session_state.current_ship_index]
                                st.session_state.message = f"Double-click {next_len} cells on your board to place your next ship."
                        else:
                            st.session_state.error = "❌ Cells must be in a straight line and adjacent. Try again."
                            st.session_state.current_ship_cells = []

# Place opponent ships once player is ready
if st.session_state.phase == "ready" and not st.session_state.opponent_ships:
    def place_opponent_ships():
        board = np.zeros((grid_size, grid_size), dtype=int)
        ships = []
        for length in ship_lengths:
            placed = False
            while not placed:
                r, c = np.random.randint(0, grid_size, size=2)
                horizontal = np.random.rand() > 0.5
                if horizontal and c + length <= grid_size and np.all(board[r, c:c+length] == 0):
                    board[r, c:c+length] = 1
                    ships.append([(r, i) for i in range(c, c+length)])
                    placed = True
                elif not horizontal and r + length <= grid_size and np.all(board[r:r+length, c] == 0):
                    board[r:r+length, c] = 1
                    ships.append([(i, c) for i in range(r, r+length)])
                    placed = True
        return board, ships

    st.session_state.opponent_board, st.session_state.opponent_ships = place_opponent_ships()

# Show opponent board (visual only for now)
st.subheader("Opponent Board (hidden ships for now)")
for row in range(grid_size):
    cols = st.columns(grid_size)
    for col in range(grid_size):
        if st.session_state.opponent_board[row, col] == 1:
            label = "❓"  # Ship is there but hidden
        else:
            label = " "
        cols[col].button(label, key=f"opponent_{row}_{col}", disabled=True)

# Show player board for debugging
st.subheader("Your Board")
handle_player_grid()

with st.expander("Debug: Show Player Board Array"):
    st.write(st.session_state.player_board.astype(int))

with st.expander("Debug: Show Opponent Board Array"):
    st.write(st.session_state.opponent_board.astype(int))
