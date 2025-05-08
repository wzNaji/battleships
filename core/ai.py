import random
import numpy as np
from core.config import grid_size, ship_lengths


# ----------------------------------------------------------------------------- #
# Internal helpers                                                              #
# ----------------------------------------------------------------------------- #
def _build_probability_grid(
    computer_guesses: np.ndarray,
    hits: list[tuple[int, int]],
    remaining_lengths: list[int],
) -> np.ndarray:
    """
    Return a heat-map where each cell’s value is the number of *legal* placements
    of the remaining ships that include that cell.

    A placement is legal if
      * it fits on the board,
      * it does not overlap a known miss,
      * it includes every still-live hit.
    """
    prob = np.zeros_like(computer_guesses, dtype=int)

    for length in remaining_lengths:
        # Horizontal placements -------------------------------------------------
        for r in range(grid_size):
            for c in range(grid_size - length + 1):
                cells = [(r, cc) for cc in range(c, c + length)]

                # Crosses a known miss?
                if any(
                    computer_guesses[x, y] == 1 and (x, y) not in hits
                    for x, y in cells
                ):
                    continue

                # Must contain all current hits
                if not all(h in cells for h in hits):
                    continue

                for x, y in cells:
                    if computer_guesses[x, y] == 0:
                        prob[x, y] += 1

        # Vertical placements ---------------------------------------------------
        for c in range(grid_size):
            for r in range(grid_size - length + 1):
                cells = [(rr, c) for rr in range(r, r + length)]
                if any(
                    computer_guesses[x, y] == 1 and (x, y) not in hits
                    for x, y in cells
                ):
                    continue
                if not all(h in cells for h in hits):
                    continue
                for x, y in cells:
                    if computer_guesses[x, y] == 0:
                        prob[x, y] += 1

    return prob


# ----------------------------------------------------------------------------- #
# Public API – called from UI                                                   #
# ----------------------------------------------------------------------------- #
def get_computer_target(
    computer_hits: list[tuple[int, int]],
    computer_guesses: np.ndarray,
    grid_size: int = grid_size,
    remaining_lengths: list[int] | None = None,
) -> tuple[int, int]:
    """
    Choose the computer’s next guess.

    * **Hunt mode** – build a probability grid from *remaining_lengths*.
    * **Target mode** – if there are live hits, boost their four neighbours.

    Ties are broken randomly so the bot’s play remains varied.
    """
    if remaining_lengths is None:
        remaining_lengths = ship_lengths

    # 1) Build base heat-map ----------------------------------------------------
    prob = _build_probability_grid(computer_guesses, computer_hits, remaining_lengths)

    # 2) Target mode boost ------------------------------------------------------
    if computer_hits:
        for hr, hc in computer_hits:
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = hr + dr, hc + dc
                if (
                    0 <= nr < grid_size
                    and 0 <= nc < grid_size
                    and computer_guesses[nr, nc] == 0
                ):
                    prob[nr, nc] += 5  # strong nudge to finish that ship

    # 3) First move fallback – checkerboard -------------------------------------
    if prob.max() == 0:
        prob = np.fromfunction(
            lambda r, c: ((r + c) % 2 == 0).astype(int), (grid_size, grid_size)
        )
        prob[computer_guesses == 1] = 0

    # 4) Random choice among best candidates ------------------------------------
    best_score = prob.max()
    candidates = np.argwhere(prob == best_score)
    r, c = random.choice(candidates)
    return int(r), int(c)
