import streamlit as st
import numpy as np
from core.config import grid_size, ship_lengths
from core.game_logic import place_opponent_ships
from core.ui import render_opponent_board, render_player_board, title_and_message

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
title_and_message()
if st.session_state.error:
    st.error(st.session_state.error)

# --- Opponent ship placement ---
if st.session_state.phase == "playing" and not st.session_state.opponent_ships:
    st.session_state.opponent_board, st.session_state.opponent_ships = place_opponent_ships()

# --- Opponent board and gameplay logic ---
if st.session_state.phase == "playing":
    render_opponent_board()
    

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
render_player_board()

# --- Debug info ---
with st.expander("Debug: Show Player Board Array"):
    st.write(st.session_state.player_board.astype(int))

with st.expander("Debug: Show Opponent Board Array"):
    st.write(st.session_state.opponent_board.astype(int))
    st.write("Opponent ships:", st.session_state.opponent_ships)
    st.write("Your guesses:", st.session_state.guesses.astype(int))
    st.write("Computer guesses:", st.session_state.computer_guesses.astype(int))
    st.write("Computer hits:", st.session_state.computer_hits)
