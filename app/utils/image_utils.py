"""
app/utils/image_utils.py
--------------------------
Handles everything about an uploaded image BEFORE it reaches the model:
validating it's actually a real image, saving it to disk with a safe
filename, and converting it into the numeric array the CNN expects.
"""

import os
import uuid

import numpy as np
from PIL import Image, UnidentifiedImageError
from werkzeug.utils import secure_filename

import config


class InvalidImageError(Exception):
    """Raised when an uploaded file isn't a valid, usable image."""
    pass


def is_allowed_extension(filename: str) -> bool:
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in config.ALLOWED_EXTENSIONS


def validate_and_open_image(file_storage) -> Image.Image:
    """
    Validate an uploaded file (a Flask FileStorage object) and return it as
    a PIL Image. Raises InvalidImageError with a human-readable message on
    anything wrong, so routes.py can show a friendly error instead of a
    stack trace.
    """
    if file_storage is None or file_storage.filename == "":
        raise InvalidImageError("No file was selected.")

    if not is_allowed_extension(file_storage.filename):
        allowed = ", ".join(sorted(config.ALLOWED_EXTENSIONS))
        raise InvalidImageError(f"Unsupported file type. Allowed types: {allowed}.")

    # Check file size without loading the whole thing into memory first.
    file_storage.seek(0, os.SEEK_END)
    size_mb = file_storage.tell() / (1024 * 1024)
    file_storage.seek(0)
    if size_mb > config.MAX_UPLOAD_SIZE_MB:
        raise InvalidImageError(f"File too large ({size_mb:.1f} MB). Max is {config.MAX_UPLOAD_SIZE_MB} MB.")

    try:
        image = Image.open(file_storage.stream)
        image.verify()  # checks the file is a genuinely valid image, not just correctly named
        file_storage.seek(0)
        image = Image.open(file_storage.stream)  # re-open: verify() consumes the file pointer
        image = image.convert("RGB")  # normalizes PNGs-with-alpha, grayscale, etc. to 3 channels
    except (UnidentifiedImageError, OSError):
        raise InvalidImageError("This file isn't a valid or readable image.")

    return image


def save_uploaded_image(image: Image.Image, original_filename: str) -> str:
    """
    Save the image to app/static/uploads/ with a collision-safe filename.
    Returns the filename (not full path) so it can be stored in history
    and referenced in templates as /static/uploads/<filename>.
    """
    safe_name = secure_filename(original_filename)
    unique_name = f"{uuid.uuid4().hex[:10]}_{safe_name}"
    save_path = os.path.join(config.UPLOAD_DIR, unique_name)
    image.save(save_path)
    return unique_name


def preprocess_image(image: Image.Image) -> np.ndarray:
    """
    Convert a PIL Image into the (1, H, W, 3) float array the model expects.

    Note: we do NOT divide by 255 here — the model itself has a Rescaling
    layer as its first layer (see model/model_architecture.py), so raw
    0-255 pixel values go straight in. Keeping rescaling INSIDE the model
    means training and inference can never accidentally use different
    preprocessing.
    """
    resized = image.resize((config.IMG_WIDTH, config.IMG_HEIGHT))
    array = np.array(resized, dtype=np.float32)
    return np.expand_dims(array, axis=0)  # add batch dimension -> (1, H, W, 3)