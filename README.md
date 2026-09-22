# AnimalVision AI

A full-stack animal image-classification project that trains a custom convolutional neural network and serves predictions through a Flask web application.

Unlike a pretrained-model demo, the classifier architecture and training pipeline are implemented in this repository and trained on the Animals-10 dataset.

## Features

- Ten-class animal image classification
- Custom TensorFlow/Keras CNN with data augmentation
- Reproducible train, validation, and test split
- Checkpointing, early stopping, and learning-rate reduction
- Saved class names and training history
- Evaluation metrics, confusion matrix, and learning curves
- Flask interface for image upload and inference
- Local prediction history and a model-performance page
- File-type and upload-size validation

## Project structure

| Path | Purpose |
|---|---|
| `model/model_architecture.py` | CNN architecture and compilation |
| `model/data_loader.py` | Dataset discovery, splitting, and input pipelines |
| `model/train.py` | Training orchestration and learning curves |
| `model/evaluate.py` | Test-set metrics and confusion matrix |
| `app/` | Flask routes, templates, static assets, and inference helpers |
| `config.py` | Paths, image settings, and training hyperparameters |
| `run.py` | Web application entry point |

## Setup

Requirements: Python 3.10 or 3.11 is recommended for TensorFlow 2.16 compatibility.

```bash
python -m venv .venv
```

Activate the environment, then install dependencies:

```bash
python -m pip install -r requirements.txt
```

## Dataset

Download the [Animals-10 dataset](https://www.kaggle.com/datasets/alessiocorrado99/animals10) and place the extracted class folders under `data/raw/`.

The data loader translates the original class-folder names, creates deterministic train/validation/test directories, and reuses an existing processed split on later runs.

## Train and evaluate

```bash
python -m model.train
python -m model.evaluate
```

Training writes the best model, class labels, history, plots, and evaluation artifacts to the configured local output paths.

## Run the web app

After training:

```bash
python run.py
```

Open `http://localhost:5000`.

If no trained model is available, the interface remains accessible but prediction requests return a clear setup message.

## Model scope

This is an educational image classifier, not a wildlife-safety or scientific identification system. Predictions depend on the training data and should not be treated as expert identification.

## Tech stack

Python · TensorFlow/Keras · Flask · NumPy · Pillow · scikit-learn · Matplotlib · Seaborn
