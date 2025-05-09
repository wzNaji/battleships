import numpy as np
from keras.models import load_model ## virker men muligvis en misconfig i interpreter
from core.config import grid_size  # reuse the constant

MODEL_PATH = "ml/model.keras"
_model = load_model(MODEL_PATH)


def predict_target(board_flat: list[int]) -> tuple[int, int]:
    """
    Choose the (row, col) that the DNN rates as most likely to be a hit.
    board_flat must be length-25 (0 = un-guessed, 1 = already guessed).
    """
    best_score, best_move = -1.0, (0, 0)

    # Pre-convert to numpy once for speed
    board_array = np.array([board_flat], dtype=np.float32)  # shape (1, 25)

    # Because the model was trained ONLY on the board state,
    # the prediction is the same for every candidate cell.
    # We’ll pick the **first** un-guessed cell when score > threshold,
    # otherwise fall back to a random un-guessed cell.

    hit_prob = float(_model.predict(board_array, verbose=0)[0][0])

    if hit_prob >= 0.5:                        # confident in a hit
        for idx, val in enumerate(board_flat):
            if val == 0:                       # first free cell
                r, c = divmod(idx, grid_size)
                return r, c
    else:                                      # low confidence → random shot
        free_indices = [i for i, v in enumerate(board_flat) if v == 0]
        choice       = np.random.choice(free_indices)
        return divmod(choice, grid_size)
