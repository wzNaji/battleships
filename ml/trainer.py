import numpy as np
import pandas as pd
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.models import load_model
from sklearn.model_selection import train_test_split
import os

# --- Load the dataset ---
DATA_PATH = "ml/dataset.csv"

if not os.path.exists(DATA_PATH):
    raise FileNotFoundError("No dataset found. Play some games first to generate ml/dataset.csv.")

# Assumes: 25 flattened cells + row + col + hit (total 28 columns)
data = pd.read_csv(DATA_PATH, header=None)

# --- Prepare features (X) and labels (y) ---
X = data.iloc[:, :25].values  # only take the first 25
y = data.iloc[:, 27].values   # last column is hit or miss

# --- Split data into training and test sets ---
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# --- Define a simple Deep Neural Network model ---
model = Sequential([
    Dense(64, activation='relu', input_shape=(25,)),
    Dense(32, activation='relu'),
    Dense(1, activation='sigmoid')  # Output layer for binary classification
])

model.compile(
    optimizer='adam',
    loss='binary_crossentropy',
    metrics=['accuracy']
)

# --- Train the model ---
print("Training model...")
model.fit(
    X_train,
    y_train,
    epochs=10,
    batch_size=8,
    validation_data=(X_test, y_test)
)

# --- Save the trained model ---
MODEL_PATH = "ml/model.keras"
model.save(MODEL_PATH)
print(f"Model saved to: {MODEL_PATH}")
