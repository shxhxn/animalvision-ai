"""
The `model` package contains everything related to the CNN itself:
loading data, defining the architecture, training, and evaluating.
It has no knowledge of Flask or the web app — that separation means the
model pipeline can be run, tested, and reasoned about completely
independently of the web layer.
"""