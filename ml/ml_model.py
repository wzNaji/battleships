# core/ml_model.py
import numpy as np
from tensorflow.keras.models import load_model

MODEL_PATH = "ml/model.keras"
_model = load_model(MODEL_PATH)

def predict_target(board_flat: list[int]) -> tuple[int, int]:
    """
    Given a flat 5x5 board (25 ints), return the predicted (row, col) to fire at.
    """
    # Try all cells not yet guessed and find the one with highest predicted score
    best_score = -1
    best_move = None
    for r in range(5):
        for c in range(5):
            idx = r * 5 + c
            if board_flat[idx] == 0:  # only try unguessed cells
                sample = np.array([board_flat + [r, c]], dtype=np.float32)
                score = _model.predict(sample, verbose=0)[0][0]
                if score > best_score:
                    best_score = score
                    best_move = (r, c)
    return best_move
