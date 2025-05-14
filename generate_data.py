# generate_data.py

import csv
import numpy as np
from core.config import grid_size, ship_lengths
from core.game_logic import place_opponent_ships, all_ships_sunk
from core.ai      import _build_probability_grid

UNKNOWN = 0
MISS    = 1
HIT     = 2

def play_one_game(writer):
    # 1) Randomly place ships for “opponent” (this is Bot B’s ships)
    board, ships = place_opponent_ships()

    # 2) Initialize Bot A’s memory of the board:
    guesses = np.zeros((grid_size, grid_size), dtype=int)  # 0=unknown,1=miss,2=hit
    hits    = []       # list of (r,c) it has hit but not yet “sunk”
    remaining = ship_lengths.copy()

    # 3) Loop until Bot A sinks all of Bot B’s ships
    while not all_ships_sunk(ships, guesses):
        # a) Board state stays the same
        flat_state = guesses.flatten().tolist()

        # b) Build probability grid exactly like the heuristic did
        prob        = _build_probability_grid(guesses, hits, remaining)
        prob[hits] += 5                      # neighbour boost (same as before)
        if prob.max() == 0:                  # checkerboard fallback
            prob = np.fromfunction(
                lambda r, c: ((r + c) % 2 == 0).astype(int), (grid_size, grid_size)
            )

        # c) Normalise to a true distribution
        heat = prob.flatten().astype("float32")
        heat = heat / heat.sum()

        # d) Pick move **from** that distribution – keeps behaviour identical
        choice = np.random.choice(25, p=heat)
        r, c   = divmod(choice, grid_size)
        hit_flag = int(board[r, c] == 1)

        # e) Log X (=25 state ints) + y (=25 heat values)
        writer.writerow(flat_state + heat.tolist())


        # d) Actually “make the shot” on Bot B’s board
        if board[r, c] == 1:
            guesses[r, c] = HIT
            hits.append((r, c))
            # If that shot completed (sunk) a ship, remove that length
            for ship in ships:
                if all(guesses[x, y] == HIT for x, y in ship) and len(ship) in remaining:
                    remaining.remove(len(ship))
                    # and clear those from hits so we don’t boost them again
                    hits = [h for h in hits if h not in ship]
        else:
            guesses[r, c] = MISS

    # Game over for this one round!

def main(num_games=200000, out_path="ml/dataset.csv"):
    # Create (or overwrite) the CSV file
    with open(out_path, "w", newline="") as f:
        writer = csv.writer(f)
        # No header; each row is: 25 state values, r, c
        for i in range(num_games):
            play_one_game(writer)
            if (i+1) % 500 == 0:
                print(f"  → {i+1} games done")

if __name__ == "__main__":
    main()
