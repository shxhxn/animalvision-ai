"""
app/routes.py
--------------
All URL routes for the app, grouped into a single Blueprint. Each view
function stays thin: it reads the request, calls out to app/utils/ or
model/ for the actual work, and renders a template. Business logic
(preprocessing, prediction, history storage) intentionally lives OUTSIDE
this file so routes.py stays easy to scan.
"""

import json
import os

from flask import Blueprint, render_template, request, jsonify, current_app

import config
from app.utils.image_utils import validate_and_open_image, save_uploaded_image, preprocess_image, InvalidImageError
from app.utils.model_utils import get_prediction, is_model_loaded
from app.utils.history_utils import add_history_entry, get_all_history, clear_history

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    """Home page: upload form + (after a prediction) the result panel."""
    return render_template("index.html", model_ready=is_model_loaded())


@main_bp.route("/predict", methods=["POST"])
def predict():
    """
    Handles an image upload, runs it through the model, saves the result to
    history, and returns JSON (the frontend calls this via fetch() so it can
    show a loading spinner and update the page without a full reload).
    """
    if not is_model_loaded():
        return jsonify({
            "error": "No trained model is available yet. Run `python -m model.train` first."
        }), 503

    try:
        image = validate_and_open_image(request.files.get("image"))
    except InvalidImageError as exc:
        return jsonify({"error": str(exc)}), 400

    saved_filename = save_uploaded_image(image, request.files["image"].filename)
    image_array = preprocess_image(image)
    prediction = get_prediction(image_array, top_k=5)
    add_history_entry(saved_filename, prediction)

    return jsonify({
        "image_url": f"/static/uploads/{saved_filename}",
        "predicted_class": prediction["predicted_class"],
        "confidence": prediction["confidence"],
        "top_predictions": prediction["top_predictions"],
    })


@main_bp.route("/history")
def history():
    """Shows every past prediction, most recent first."""
    entries = get_all_history()
    return render_template("history.html", entries=entries)


@main_bp.route("/history/clear", methods=["POST"])
def history_clear():
    clear_history()
    return jsonify({"status": "cleared"})


@main_bp.route("/about")
def about():
    """Static page explaining how the CNN works, for non-technical visitors and recruiters alike."""
    return render_template("about.html")


@main_bp.route("/metrics")
def metrics():
    """
    Model performance page: accuracy/loss curves, confusion matrix,
    precision/recall/F1. Reads whatever evaluate.py + train.py last wrote
    to static/results/ — this route does no computation of its own.
    """
    metrics_data = None
    if os.path.exists(config.METRICS_JSON_PATH):
        with open(config.METRICS_JSON_PATH) as f:
            metrics_data = json.load(f)

    history_data = None
    if os.path.exists(config.TRAINING_HISTORY_PATH):
        with open(config.TRAINING_HISTORY_PATH) as f:
            history_data = json.load(f)

    return render_template(
        "metrics.html",
        metrics=metrics_data,
        training_history=history_data,
        has_results=metrics_data is not None,
    )


@main_bp.route("/retrain", methods=["POST"])
def retrain():
    """
    Kicks off a fresh training run using whatever's currently in data/raw/.
    This is intentionally synchronous and simple (fine for a portfolio demo
    run locally); the README notes that a production version would move
    this to a background job queue (e.g. Celery) so an HTTP request isn't
    held open for the many minutes training can take.
    """
    from model.train import run_training
    from app.utils.model_utils import load_model_and_classes

    try:
        run_training()
    except Exception as exc:  # noqa: BLE001 - surfacing any training failure to the caller
        return jsonify({"error": f"Training failed: {exc}"}), 500

    # Force a reload of the newly trained model into memory.
    import app.utils.model_utils as model_utils
    model_utils._model = None
    model_utils._class_names = None
    load_model_and_classes()

    return jsonify({"status": "Training complete. New model is now live."})