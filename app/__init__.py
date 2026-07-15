"""
app/__init__.py
-----------------
The Flask "application factory". Instead of creating the Flask app as a
bare module-level variable, we wrap creation in a function (create_app).

Why this pattern: it lets us create multiple app instances with different
configs (e.g. one for running the real server, one for tests with a mocked
model), and it avoids circular-import headaches since routes are registered
onto the app AFTER it exists, not imported at module load time.
"""

from flask import Flask

import config
from app.utils.model_utils import load_model_and_classes


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = config.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    # Load the trained model ONCE at startup, not per-request. If no model
    # has been trained yet, we don't crash the whole app — we let it start
    # so the user can still see the UI, and routes.py will show a friendly
    # "model not trained yet" message instead of a 500 error.
    try:
        load_model_and_classes()
    except FileNotFoundError as exc:
        print(f"[app] WARNING: {exc}")

    from app.routes import main_bp
    app.register_blueprint(main_bp)

    return app