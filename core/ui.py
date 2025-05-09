from __future__ import annotations

import streamlit as st
from core.config import grid_size, ship_lengths
from core.game_logic import is_valid_ship_selection, all_ships_sunk
from core.ai import get_computer_target
import csv


# -----------------------------------------------------------------------------
# Helper utilities                                                              
# -----------------------------------------------------------------------------

def _remaining_lengths(player_ships: list[list[tuple[int, int]]], guesses) -> list[int]:
    """Lengths of the player’s ships that are not yet fully guessed."""
    lengths = [
        len(ship)
        for ship in player_ships
        if not all(guesses[r, c] == 1 for r, c in ship)
    ]
    return lengths or [1]  # never return empty list


def _prune_sunk_hits(
    computer_hits: list[tuple[int, int]],
    player_ships: list[list[tuple[int, int]]],
    guesses,
) -> None:
    """Remove any hit cells that belong to ships that have just been sunk."""
    for ship in player_ships:
        if all(guesses[r, c] == 1 for r, c in ship):
            for cell in ship:
                if cell in computer_hits:
                    computer_hits.remove(cell)


# -----------------------------------------------------------------------------
# Public UI functions                                                           
# -----------------------------------------------------------------------------

def title_and_message():
    st.title("Battleships!")
    st.write(st.session_state.message)


def render_player_board():
    """Draw the player's own grid and handle ship placement."""
    for row in range(grid_size):
        cols = st.columns(grid_size)
        for col in range(grid_size):
            key = f"cell_{row}_{col}"

            # -----------------------------------------------------------------
            # Placement phase --------------------------------------------------
            # -----------------------------------------------------------------
            if st.session_state.phase == "placing":
                if st.session_state.player_board[row, col] == 1:
                    label = "🚢"
                elif (row, col) in st.session_state.current_ship_cells:
                    label = "✅"
                else:
                    label = " "

                if cols[col].button(label, key=key):
                    # -- Ignore re‑click on the same cell ---------------------
                    if (row, col) in st.session_state.current_ship_cells:
                        return

                    # -- Register the click -----------------------------------
                    st.session_state.current_ship_cells.append((row, col))
                    required = ship_lengths[st.session_state.current_ship_index]

                    # -- Ship complete? ---------------------------------------
                    if len(st.session_state.current_ship_cells) == required:
                        if is_valid_ship_selection(st.session_state.current_ship_cells):
                            # Commit the ship to the board/state
                            for r, c in st.session_state.current_ship_cells:
                                st.session_state.player_board[r, c] = 1
                            st.session_state.player_ships.append(
                                st.session_state.current_ship_cells
                            )
                            st.session_state.current_ship_cells = []
                            st.session_state.current_ship_index += 1
                            st.session_state.error = ""

                            if (
                                st.session_state.current_ship_index
                                == len(ship_lengths)
                            ):
                                st.session_state.phase = "playing"
                                st.session_state.message = (
                                    "🎯 Start guessing: click on opponent's board!"
                                )
                            else:
                                next_len = ship_lengths[
                                    st.session_state.current_ship_index
                                ]
                                st.session_state.message = (
                                    f"Double-click {next_len} cells on your board to place your next ship."
                                )
                        else:
                            st.session_state.error = (
                                "❌ Cells must be in a straight line and adjacent."
                            )
                            st.session_state.current_ship_cells = []

                    # -- Immediate visual feedback ---------------------------
                    st.rerun()

            # -----------------------------------------------------------------
            # Gameplay / Endgame phases ---------------------------------------
            # -----------------------------------------------------------------
            else:
                if st.session_state.computer_guesses[row, col] == 1:
                    label = "💥" if st.session_state.player_board[row, col] == 1 else "❌"
                elif st.session_state.player_board[row, col] == 1:
                    label = "🚢"
                else:
                    label = " "
                cols[col].button(label, key=key, disabled=True)


def render_opponent_board():
    """Draw the opponent grid and handle the player's firing clicks."""
    st.subheader("Opponent Board (click to guess)")
    for row in range(grid_size):
        cols = st.columns(grid_size)
        for col in range(grid_size):
            key = f"opponent_{row}_{col}"

            # Already guessed --------------------------------------------------
            if st.session_state.guesses[row, col] == 1:
                label = (
                    "✅"
                    if any((row, col) in s for s in st.session_state.opponent_ships)
                    else "❌"
                )
                cols[col].button(label, key=key, disabled=True)
                continue

            # Fresh cell -------------------------------------------------------
            if cols[col].button(" ", key=key):
                # -----------------------------------------------------------------
                # 1) Player fires ---------------------------------------------------
                # -----------------------------------------------------------------
                st.session_state.guesses[row, col] = 1

                hit_ship = next(
                    (
                        i
                        for i, s in enumerate(st.session_state.opponent_ships)
                        if (row, col) in s
                    ),
                    None,
                )
                if hit_ship is not None:
                    st.session_state.message = f"🎯 Hit at ({row}, {col})! 💥"
                    if all(
                        st.session_state.guesses[r, c] == 1
                        for r, c in st.session_state.opponent_ships[hit_ship]
                    ):
                        if hit_ship not in st.session_state.sunk_ships:
                            st.session_state.sunk_ships.add(hit_ship)
                            st.toast("🔥 You sunk a ship!", icon="🚢")
                else:
                    st.session_state.message = f"💦 Miss at ({row}, {col})!"

                # Win check ------------------------------------------------------
                if all_ships_sunk(
                    st.session_state.opponent_ships, st.session_state.guesses
                ):
                    st.session_state.phase = "won"
                    st.session_state.message = "🏆 You sank all opponent ships!"
                    st.rerun()

                # -----------------------------------------------------------------
                # 2) Computer fires ------------------------------------------------
                # -----------------------------------------------------------------
                remaining = _remaining_lengths(
                    st.session_state.player_ships, st.session_state.computer_guesses
                )
                r, c = get_computer_target(
                    st.session_state.computer_hits,
                    st.session_state.computer_guesses,
                    grid_size,
                    remaining_lengths=remaining,
                )
                st.session_state.computer_guesses[r, c] = 1

                # --- Log training data for DNN ---

                with open("ml/dataset.csv", "a", newline="") as f:
                    writer = csv.writer(f)
                    board_flat = st.session_state.computer_guesses.flatten().astype(int).tolist()
                    writer.writerow(board_flat + [r, c, int(st.session_state.player_board[r, c] == 1)])


                if st.session_state.player_board[r, c] == 1:
                    st.session_state.computer_hits.append((r, c))
                    st.toast(f"🤖 Computer hit at ({r}, {c})! 💥", icon="💥")
                else:
                    st.toast(f"🤖 Computer missed at ({r}, {c})!", icon="👻")

                _prune_sunk_hits(
                    st.session_state.computer_hits,
                    st.session_state.player_ships,
                    st.session_state.computer_guesses,
                )

                # Loss check -----------------------------------------------------
                player_cells = [
                    cell for ship in st.session_state.player_ships for cell in ship
                ]
                if all(
                    st.session_state.computer_guesses[r, c] == 1 for r, c in player_cells
                ):
                    st.session_state.phase = "lost"
                    st.session_state.message = "💥 The computer sank all your ships! Game over."

                # Immediate visual feedback ------------------------------------
                st.rerun()
