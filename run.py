"""
run.py
-------
The single entry point for starting the AnimalVision AI web server.

Usage:
    python run.py
"""

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)