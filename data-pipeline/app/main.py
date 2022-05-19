# main.py
"""Entry point for data pipeline service.

This service implements a lightweight data
pipeline that scrapes, processes, and saves
data for the dashboard.

This process is invoked every morning.
"""
import os
from pipeline import Pipeline
from flask import Flask

app = Flask(__name__)


@app.route("/", methods=['GET', 'POST'])
def index():
  """Run the pipeline."""
  pipeline = Pipeline()
  status = pipeline.run()
  return ("", status)


if __name__ == "__main__":
  app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
