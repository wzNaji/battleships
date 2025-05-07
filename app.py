import streamlit as st
import numpy as np

grid_size = 5
ship_lengths = [3, 2]

if "player_board" not in st.session_state:
    st.session_state.player_board = np.zeros((grid_size, grid_size), dtype=int)
    st.session_state.player_ships = []  # list of confirmed ships
    st.session_state.current_ship_cells = []  # temp list for selecting current ship
    st.session_state.current_ship_index = 0
    st.session_state.phase = "placing"
    st.session_state.message = f"Double-click {ship_lengths[0]} cells to place your first ship."
    st.session_state.error = ""

st.title("Battleships!")

st.write(st.session_state.message)
if st.session_state.error:
    st.error(st.session_state.error)

def is_valid_ship_selection(cells):
    if len(cells) < 2: #fordi vores skibe er af længden 3 og 2.
        return True
    rows = [r for r, _ in cells]
    cols = [c for _, c in cells] # list comprehension
    same_row = all(r == rows[0] for r in rows) 
    same_col = all(c == cols[0] for c in cols) # Kontrol af samme række el. samme kolonne

    if not (same_row or same_col):
        return False # Det spiller ikke

    if same_row:
        return sorted(cols) == list(range(min(cols), max(cols) + 1)) # Kontrol af no-gaps
    if same_col:
        return sorted(rows) == list(range(min(rows), max(rows) + 1))

    return False


# Display grid
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
                    continue  # Ignore duplicates
                st.session_state.current_ship_cells.append((row, col))

                required_length = ship_lengths[st.session_state.current_ship_index]

                if len(st.session_state.current_ship_cells) == required_length:
                    if is_valid_ship_selection(st.session_state.current_ship_cells):
                        # Confirm this ship
                        for r, c in st.session_state.current_ship_cells:
                            st.session_state.player_board[r, c] = 1
                        st.session_state.player_ships.append(st.session_state.current_ship_cells)
                        st.session_state.current_ship_cells = []
                        st.session_state.current_ship_index += 1
                        st.session_state.error = ""

                        # Move to next ship or finish
                        if st.session_state.current_ship_index == len(ship_lengths):
                            st.session_state.phase = "ready"
                            st.session_state.message = "✅ All ships placed! Ready to play!"
                        else:
                            next_len = ship_lengths[st.session_state.current_ship_index]
                            st.session_state.message = f"Double-click {next_len} cells to place your next ship."
                    else:
                        st.session_state.error = "❌ Cells must be in a straight line and adjacent. Try again."
                        st.session_state.current_ship_cells = []


# for at debug
with st.expander("Show My Board"):
    st.write(st.session_state.player_board.astype(int))
    
