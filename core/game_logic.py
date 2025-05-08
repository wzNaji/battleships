from core.config import grid_size, ship_lengths
import numpy as np

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
    

def all_ships_sunk(ships, guesses):
    return all(all(guesses[r, c] == 1 for r, c in ship) for ship in ships)