# ml/train_move_choice.py
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.metrics import TopKCategoricalAccuracy
from sklearn.model_selection import train_test_split
import os
from core.config import grid_size

# --- Load the dataset ---
DATA_PATH = "ml/dataset.csv"
if not os.path.exists(DATA_PATH):
    raise FileNotFoundError("No dataset found. Play some games first to generate ml/dataset.csv.")

data = pd.read_csv(DATA_PATH, header=None)
# Drop any incomplete rows
data = data.dropna(how="any")

# --- Prepare features (X) and move-choice labels (y) ---
# X = first 25 columns (board), still 0/1/2 divided by 2
X = data.iloc[:, :25].values.astype("float32") / 2.0

# y = next 25 columns -- the normalised heat-map you saved in generate_data.py
y = data.iloc[:, 25:50].values.astype("float32")


# --- Split into train/test ---
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# --- Build a move-choice classifier ---
model = Sequential([
    Dense(128, activation='relu', input_shape=(25,)),
    Dense(64, activation='relu'),
    Dense(grid_size * grid_size, activation='softmax')
])

# ── Metrics ───────────────────────────────────────────────────────────────
# “top-10 accuracy” = did the net put probability mass on ANY of the 10
# cells that the target distribution marks?
top10 = TopKCategoricalAccuracy(k=10, name="top10")

# ── Compile ───────────────────────────────────────────────────────────────
model.compile(
    optimizer="adam",
    loss="kl_divergence",   # KL ⇒ optimum loss is *0* instead of ~2.30
    metrics=[top10]         # you can add more if you like
)


# --- Train ---
print("Training move-choice model...")
model.fit(
    X_train, y_train,
    epochs=20,
    batch_size=32,
    validation_data=(X_test, y_test)
)

# --- Save the model ---
MODEL_PATH = "ml/model_move_choice.keras"
model.save(MODEL_PATH)
print(f"Move-choice model saved to: {MODEL_PATH}")
