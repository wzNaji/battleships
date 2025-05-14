import numpy as np
from tensorflow.keras.models import load_model
from core.config import grid_size

MODEL_PATH = "ml/model_move_choice.keras"
model = load_model(MODEL_PATH)

def predict_move(board_flat: list[int]) -> tuple[int, int]:
    """
    board_flat: 25-length list with
        0 = unknown, 1 = miss, 2 = hit.

    Returns (row, col) picked by the network.
    Already-guessed cells are masked out, then we *sample*
    from the remaining probability mass so play stays varied.
    """
    # 1) normalise exactly like during training
    x = (np.array(board_flat, dtype=np.float32) / 2.0).reshape(1, -1)

    # 2) full 25-cell heat-map from the model
    heat = model.predict(x, verbose=0)[0]          # shape (25,)

    # 3) mask cells that were already tried
    for idx, val in enumerate(board_flat):
        if val != 0:                               # miss or hit
            heat[idx] = 0.0

    # 4) re-normalise (all-zero can happen only if the board is full)
    s = heat.sum()
    if s == 0:
        raise ValueError("No legal moves left")
    heat /= s

    # ε-greedy: 10 % explore, 90 % exploit
    if np.random.rand() < 0.10:            # 0.10 = epsilon
        choice = int(np.random.choice(25, p=heat))   # explore
    else:
        choice = int(np.argmax(heat))                 # exploit (best cell)

    return divmod(choice, grid_size)

