"""
app/utils/history_utils.py
----------------------------
Persists every prediction the app makes, so the History page can show past
uploads and results.

We use a simple JSON file rather than a database. For a project this size
that's a deliberate, defensible choice: zero setup, human-readable, easy to
inspect/reset. The README calls out SQLite as the natural next step if this
were a multi-user production app (JSON files aren't safe under concurrent
writes) — worth knowing the limitation even when the simple choice is right
for now.
"""

import json
import os
from datetime import datetime

import config


def _read_history() -> list:
    if not os.path.exists(config.HISTORY_DB_PATH):
        return []
    with open(config.HISTORY_DB_PATH) as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            # A corrupted/empty history file shouldn't crash the app.
            return []


def _write_history(history: list) -> None:
    with open(config.HISTORY_DB_PATH, "w") as f:
        json.dump(history, f, indent=2)


def add_history_entry(image_filename: str, prediction: dict) -> None:
    """
    Append one prediction result to history. Newest entries are inserted
    at the front so the History page can display them without re-sorting.
    """
    history = _read_history()
    entry = {
        "id": len(history) + 1,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "image_filename": image_filename,
        "predicted_class": prediction["predicted_class"],
        "confidence": prediction["confidence"],
        "top_predictions": prediction["top_predictions"],
    }
    history.insert(0, entry)
    _write_history(history)


def get_all_history() -> list:
    return _read_history()


def clear_history() -> None:
    _write_history([])