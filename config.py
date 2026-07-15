"""
config.py
---------
Single source of truth for project-wide settings.

Why this file exists (SE principle: "Don't Repeat Yourself" / avoid magic numbers):
Instead of hardcoding paths, image sizes, or hyperparameters in five different
files, every module imports its settings from here. If we later change the
image size, the number of training epochs, or where the model is saved, we
change it in exactly ONE place.
"""

import os

# ---------------------------------------------------------------------------
# Base paths
# ---------------------------------------------------------------------------
# BASE_DIR = the absolute path to the project root (wherever this file lives).
# Using an absolute path computed at runtime (instead of a hardcoded string)
# means the project works no matter where it's cloned to on disk.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")          # original dataset, untouched
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "processed")  # train/val/test split

MODEL_DIR = os.path.join(BASE_DIR, "model")
SAVED_MODEL_DIR = os.path.join(MODEL_DIR, "saved")
MODEL_PATH = os.path.join(SAVED_MODEL_DIR, "animal_cnn.keras")
CLASS_NAMES_PATH = os.path.join(SAVED_MODEL_DIR, "class_names.json")
TRAINING_HISTORY_PATH = os.path.join(SAVED_MODEL_DIR, "training_history.json")

STATIC_RESULTS_DIR = os.path.join(BASE_DIR, "static", "results")
CONFUSION_MATRIX_PATH = os.path.join(STATIC_RESULTS_DIR, "confusion_matrix.png")
ACCURACY_PLOT_PATH = os.path.join(STATIC_RESULTS_DIR, "accuracy_plot.png")
LOSS_PLOT_PATH = os.path.join(STATIC_RESULTS_DIR, "loss_plot.png")
METRICS_JSON_PATH = os.path.join(STATIC_RESULTS_DIR, "metrics.json")

UPLOAD_DIR = os.path.join(BASE_DIR, "app", "static", "uploads")
HISTORY_DB_PATH = os.path.join(BASE_DIR, "app", "static", "history.json")

# ---------------------------------------------------------------------------
# Image / model settings
# ---------------------------------------------------------------------------
IMG_HEIGHT = 128
IMG_WIDTH = 128
IMG_CHANNELS = 3
BATCH_SIZE = 32

# Animals-10 dataset classes (translated from Italian folder names to English).
# This mapping is used by data_loader.py to rename folders on first load.
ANIMALS10_TRANSLATE = {
    "cane": "dog",
    "cavallo": "horse",
    "elefante": "elephant",
    "farfalla": "butterfly",
    "gallina": "chicken",
    "gatto": "cat",
    "mucca": "cow",
    "pecora": "sheep",
    "ragno": "spider",
    "scoiattolo": "squirrel",
}

# ---------------------------------------------------------------------------
# Training hyperparameters
# ---------------------------------------------------------------------------
EPOCHS = 25
LEARNING_RATE = 1e-3
VALIDATION_SPLIT = 0.15
TEST_SPLIT = 0.15
RANDOM_SEED = 42

# ---------------------------------------------------------------------------
# Upload validation
# ---------------------------------------------------------------------------
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
MAX_UPLOAD_SIZE_MB = 10

# ---------------------------------------------------------------------------
# Ensure critical directories exist at import time.
# This means any script that does `import config` automatically guarantees
# these folders are present, instead of every script re-implementing
# os.makedirs checks.
# ---------------------------------------------------------------------------
for directory in [SAVED_MODEL_DIR, STATIC_RESULTS_DIR, UPLOAD_DIR, PROCESSED_DATA_DIR]:
    os.makedirs(directory, exist_ok=True)