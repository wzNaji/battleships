import streamlit as st
import numpy as np
import random

grid_size = 5
ship_lengths = [3, 2]

if "player_board" not in st.session_state:
    st.session_state.player_board = np.zeros((grid_size, grid_size), dtype=int)
    st.session_state.opponent_board = np.zeros((grid_size, grid_size), dtype=int)
    st.session_state.player_ships = []
    st.session_state.opponent_ships = []
    st.session_state.current_ship_cells = []
    st.session_state.current_ship_index = 0
    st.session_state.phase = "placing"
    st.session_state.message = f"Double-click {ship_lengths[0]} cells on your board to place your first ship."
    st.session_state.error = ""
    st.session_state.guesses = np.zeros((grid_size, grid_size), dtype=int)
    st.session_state.computer_guesses = np.zeros((grid_size, grid_size), dtype=int)
    st.session_state.sunk_ships = set()
    st.session_state.computer_hits = []

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

def handle_player_grid():
    for row in range(grid_size):
        cols = st.columns(grid_size)
        for col in range(grid_size):
            key = f"cell_{row}_{col}"
            if st.session_state.phase == "placing":
                if st.session_state.player_board[row, col] == 1:
                    label = "🚢"
                elif (row, col) in st.session_state.current_ship_cells:
                    label = "✅"
                else:
                    label = " "
                if cols[col].button(label, key=key):
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
                                st.session_state.phase = "playing"
                                st.session_state.message = "🎯 Start guessing: click on opponent's board!"
                            else:
                                next_len = ship_lengths[st.session_state.current_ship_index]
                                st.session_state.message = f"Double-click {next_len} cells on your board to place your next ship."
                        else:
                            st.session_state.error = "❌ Cells must be in a straight line and adjacent. Try again."
                            st.session_state.current_ship_cells = []
            else:
                if st.session_state.computer_guesses[row, col] == 1:
                    if st.session_state.player_board[row, col] == 1:
                        label = "💥"
                    else:
                        label = "❌"
                elif st.session_state.player_board[row, col] == 1:
                    label = "🚢"
                else:
                    label = " "
                cols[col].button(label, key=key, disabled=True)

# (rest of code unchanged)


if st.session_state.phase == "playing" and not st.session_state.opponent_ships:
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

# Show opponent board for guessing
if st.session_state.phase == "playing":
    st.subheader("Opponent Board (click to guess)")
    for row in range(grid_size):
        cols = st.columns(grid_size)
        for col in range(grid_size):
            key = f"opponent_{row}_{col}"
            guess = st.session_state.guesses[row, col]
            if guess == 1:
                if any((row, col) in ship for ship in st.session_state.opponent_ships):
                    label = "✅"
                else:
                    label = "❌"
                cols[col].button(label, key=key, disabled=True)
            else:
                if cols[col].button(" ", key=key):
                    st.session_state.guesses[row, col] = 1
                    hit = None
                    for i, ship in enumerate(st.session_state.opponent_ships):
                        if (row, col) in ship:
                            hit = i
                            break
                    if hit is not None:
                        st.session_state.message = f"🎯 Hit at ({row}, {col})! 💥"
                        ship_hit = st.session_state.opponent_ships[hit]
                        if all(st.session_state.guesses[r, c] == 1 for r, c in ship_hit):
                            if hit not in st.session_state.sunk_ships:
                                st.session_state.sunk_ships.add(hit)
                                st.toast("🔥 You sunk a ship!", icon="🚢")
                    else:
                        st.session_state.message = f"💦 Miss at ({row}, {col})!"
                    all_hit = all(all(st.session_state.guesses[r, c] == 1 for r, c in ship) for ship in st.session_state.opponent_ships)
                    if all_hit:
                        st.session_state.phase = "won"
                        st.session_state.message = "🏆 You sank all opponent ships!"
                    else:
                        # Computer's turn to guess smartly
                        def get_computer_target():
                            # Try surrounding a hit
                            for hr, hc in st.session_state.computer_hits:
                                for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
                                    nr, nc = hr+dr, hc+dc
                                    if 0 <= nr < grid_size and 0 <= nc < grid_size and st.session_state.computer_guesses[nr, nc] == 0:
                                        return nr, nc
                            # Otherwise, random
                            while True:
                                r, c = random.randint(0, grid_size - 1), random.randint(0, grid_size - 1)
                                if st.session_state.computer_guesses[r, c] == 0:
                                    return r, c

                        r, c = get_computer_target()
                        st.session_state.computer_guesses[r, c] = 1
                        if st.session_state.player_board[r, c] == 1:
                            st.session_state.computer_hits.append((r, c))
                        else:
                            st.toast(f"🤖 Computer missed at ({r}, {c})!", icon="👻")

                        # Check if computer has won
                        player_ship_cells = [cell for ship in st.session_state.player_ships for cell in ship]
                        if all(st.session_state.computer_guesses[r, c] == 1 for r, c in player_ship_cells):
                            st.session_state.phase = "lost"
                            st.session_state.message = "💥 The computer sank all your ships! Game over."

if st.session_state.phase == "won":
    st.success("Game over! You won!")
    if st.button("Restart Game"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.experimental_rerun()

if st.session_state.phase == "lost":
    st.error("Game over! You lost!")
    if st.button("Try Again"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.experimental_rerun()

st.subheader("Your Board")
handle_player_grid()

with st.expander("Debug: Show Player Board Array"):
    st.write(st.session_state.player_board.astype(int))

with st.expander("Debug: Show Opponent Board Array"):
    st.write(st.session_state.opponent_board.astype(int))
    st.write("Opponent ships:", st.session_state.opponent_ships)
    st.write("Your guesses:", st.session_state.guesses.astype(int))
    st.write("Computer guesses:", st.session_state.computer_guesses.astype(int))
    st.write("Computer hits:", st.session_state.computer_hits)
