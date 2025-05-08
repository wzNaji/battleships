from core.config import grid_size, ship_lengths
import streamlit as st
from core.game_logic import is_valid_ship_selection, all_ships_sunk
from core.ai import get_computer_target

def title_and_message():
    st.title("Battleships!")
    st.write(st.session_state.message)

def render_player_board():
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

def render_opponent_board():    
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