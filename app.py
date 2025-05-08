import streamlit as st
import numpy as np
from core.config import grid_size, ship_lengths
from core.game_logic import is_valid_ship_selection, place_opponent_ships, all_ships_sunk
from core.ai import get_computer_target

# --- Initialize session state ---
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

# --- UI Header ---
st.title("Battleships!")
st.write(st.session_state.message)
if st.session_state.error:
    st.error(st.session_state.error)

# --- Player board rendering ---
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

# --- Opponent ship placement ---
if st.session_state.phase == "playing" and not st.session_state.opponent_ships:
    st.session_state.opponent_board, st.session_state.opponent_ships = place_opponent_ships()

# --- Opponent board and gameplay logic ---
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
                        if all(st.session_state.guesses[r, c] == 1 for r, c in st.session_state.opponent_ships[hit]):
                            if hit not in st.session_state.sunk_ships:
                                st.session_state.sunk_ships.add(hit)
                                st.toast("🔥 You sunk a ship!", icon="🚢")
                    else:
                        st.session_state.message = f"💦 Miss at ({row}, {col})!"

                    if all_ships_sunk(st.session_state.opponent_ships, st.session_state.guesses):
                        st.session_state.phase = "won"
                        st.session_state.message = "🏆 You sank all opponent ships!"
                    else:
                        # Computer's turn
                        r, c = get_computer_target(st.session_state.computer_hits, st.session_state.computer_guesses, grid_size)
                        st.session_state.computer_guesses[r, c] = 1
                        if st.session_state.player_board[r, c] == 1:
                            st.session_state.computer_hits.append((r, c))
                        else:
                            st.toast(f"🤖 Computer missed at ({r}, {c})!", icon="👻")

                        player_cells = [cell for ship in st.session_state.player_ships for cell in ship]
                        if all(st.session_state.computer_guesses[r, c] == 1 for r, c in player_cells):
                            st.session_state.phase = "lost"
                            st.session_state.message = "💥 The computer sank all your ships! Game over."

# --- End game states ---
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

# --- Player board ---
st.subheader("Your Board")
handle_player_grid()

# --- Debug info ---
with st.expander("Debug: Show Player Board Array"):
    st.write(st.session_state.player_board.astype(int))

with st.expander("Debug: Show Opponent Board Array"):
    st.write(st.session_state.opponent_board.astype(int))
    st.write("Opponent ships:", st.session_state.opponent_ships)
    st.write("Your guesses:", st.session_state.guesses.astype(int))
    st.write("Computer guesses:", st.session_state.computer_guesses.astype(int))
    st.write("Computer hits:", st.session_state.computer_hits)
