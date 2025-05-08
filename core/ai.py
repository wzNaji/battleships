import random

def get_computer_target(computer_hits, computer_guesses, grid_size):
    for hr, hc in computer_hits:
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = hr + dr, hc + dc
            if 0 <= nr < grid_size and 0 <= nc < grid_size and computer_guesses[nr, nc] == 0:
                return nr, nc
    while True:
        r, c = random.randint(0, grid_size - 1), random.randint(0, grid_size - 1)
        if computer_guesses[r, c] == 0:
            return r, c
