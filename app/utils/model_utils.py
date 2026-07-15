"""
app/utils/model_utils.py
-------------------------
Everything related to loading the trained CNN and running predictions on it.

Why this is its own file: the Flask routes shouldn't need to know HOW a
prediction is made (which model class, how top-5 is computed, etc.) — they
should just call get_prediction(image) and get back a clean result. This
also means we can swap the model or change how we rank predictions without
touching routes.py at all.
"""

import json

import numpy as np
import tensorflow as tf

import config

# Module-level cache: the model is loaded ONCE when the Flask app starts,
# not on every single request. Loading a Keras model from disk takes real
# time (hundreds of ms to seconds) — doing that per-request would make the
# app painfully slow.
_model = None
_class_names = None


def load_model_and_classes():
    """
    Load the trained model and class names into memory. Called once at app
    startup (see app/__init__.py). Safe to call multiple times — it's a
    no-op after the first successful load.
    """
    global _model, _class_names

    if _model is not None:
        return _model, _class_names

    import os
    if not os.path.exists(config.MODEL_PATH):
        raise FileNotFoundError(
            f"No trained model found at {config.MODEL_PATH}. "
            "Train one first with: python -m model.train"
        )

    try:
        _model = tf.keras.models.load_model(config.MODEL_PATH)
    except (ValueError, OSError) as exc:
        raise FileNotFoundError(
            f"Could not load model at {config.MODEL_PATH} ({exc}). "
            "Try retraining with: python -m model.train"
        ) from exc

    with open(config.CLASS_NAMES_PATH) as f:
        _class_names = json.load(f)

    print(f"[model_utils] Loaded model with {len(_class_names)} classes: {_class_names}")
    return _model, _class_names


def is_model_loaded() -> bool:
    return _model is not None


def get_prediction(image_array: np.ndarray, top_k: int = 5) -> dict:
    """
    Run inference on a single preprocessed image and return a structured
    result the routes/templates can use directly.

    Args:
        image_array: a (1, IMG_HEIGHT, IMG_WIDTH, 3) float array, as
            produced by app/utils/image_utils.preprocess_image().
        top_k: how many top predictions to return.

    Returns:
        {
            "predicted_class": "dog",
            "confidence": 92.4,                     # percent, rounded
            "top_predictions": [
                {"label": "dog", "confidence": 92.4},
                {"label": "cat", "confidence": 4.1},
                ...
            ]
        }
    """
    if _model is None:
        raise RuntimeError("Model not loaded — call load_model_and_classes() at app startup.")

    raw_predictions = _model.predict(image_array, verbose=0)[0]  # shape: (num_classes,)

    # argsort ascending, then reverse to get highest-probability classes first.
    top_indices = np.argsort(raw_predictions)[::-1][:top_k]

    top_predictions = [
        {
            "label": _class_names[i],
            "confidence": round(float(raw_predictions[i]) * 100, 2),
        }
        for i in top_indices
    ]

    return {
        "predicted_class": top_predictions[0]["label"],
        "confidence": top_predictions[0]["confidence"],
        "top_predictions": top_predictions,
    } 