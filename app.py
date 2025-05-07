import streamlit as st
import numpy as np

grid_size = 5
ship_lenght = [3,2]

if "player_board" not in st.session_state:
    st.session_state.player_board = np.zeros((grid_size,grid_size), dtype=int)
    st.session_state.opponent_board = np.zeros((grid_size, grid_size), dtype=int)
    st.session_state.opponent_ships = []
    st.session_state.guesses = np.zeros((grid_size, grid_size), dtype=int)
    st.session_state.phase = "placing"
    st.session_state.player_ships = []
    st.session_state.message = "Place ur ships by clicking the cells!"

