# main.py
"""
This service does two things:

train: Use results from played games to update model weights.

forecast: generates a forecast of game results.

There is also a method for setting model parameters (e.g., to
initialize the model at the beginning of a season).

The code is written such that the model used to execute these
actions can be flexible. Each POST request should contain
a field 'model-name' in the json that specifies which model is
to be used. 

Currently, model options are:
- 'elo'
"""
import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify, Response
from typing import Tuple

from utils import load_parameters, save_parameters
from elo import ELO
from forecast import Forecaster
from model import Model


app = Flask(__name__)

load_dotenv()

@app.route("/", methods=['GET'])
def ping():
  """For testing purposes."""
  return "hello!"

@app.route("/set_parameters", methods=['POST'])
def set_parameters():
  """Set model parameters.

  Request should contain json with the following fields:
  - model-name: name of the model whose parameters will be set
  - params: dict of parameters appropriate for given model
  """
  data = request.get_json()

  model_name = data['model-name']
  params = data['params']

  env_param_name = model_name.upper() + "-BUCKET-NAME"
  bucket_name = os.getenv(env_param_name)
  if bucket_name:
    save_parameters(bucket_name, params)
    return Response("Success!", status=201, mimetype='text/plain')

  return Response("Invalid model name.", status=400, mimetype='text/plain')

def load_model(model_name: str) -> Tuple[Model, str]:
  """Load model and bucket name using model name.

  Add to this method as new models are added.
  """
  if model_name.upper() == 'ELO':
    bucket_name = os.getenv("ELO-BUCKET-NAME")
    params = load_parameters(bucket_name)
    return ELO(params), bucket_name
  else:
    return None, ""

@app.route("/train", methods=['POST'])
def train():
  """Train the model.

  Post must contain json data with the following
  data:

  - model-name: e.g., 'elo'
  - games: a list of dicts. each dict must include
    home, visitor, and date.
  - results: a list of ints of the same length as games.
  """
  # unpack request data
  data = request.get_json()

  # select the model to train
  model_name = data['model-name']
  m, bucket_name = load_model(model_name)
  if m is None:
    Response("Invalid model name", status=400, mimetype='text/plain')

  # train model and save new parameters
  m.train(data['games'], data['results'])
  save_parameters(bucket_name, m.params)

  return Response("Success!", status=201, mimetype='text/plain')

@app.route("/forecast", methods=['POST'])
def forecast():
  """Generate forecast.

  Expects the request to contain one list:

  model-name: 
  schedule: a list of games yet to be played,
    in chronological order, where each game
    is represented as a dict with keys such as
    'home', 'visitor', and 'date'.

  The response contains a list of probabilities that
  the home team won each game in the schedule. The
  order of the probabilities is the same as the order
  of the schedule.
  """
  data = request.get_json()

  # select the model for forecasting
  model_name = data['model-name']
  m, bucket_name = load_model(model_name)
  if m is None:
    Response("Invalid model name", status=400, mimetype='application/json')

  # generate forecast
  f = Forecaster(m)
  results = f.forecast(data['schedule'])
 
  # package forecast and return 
  return jsonify({'forecast': results})

if __name__ == "__main__":
  app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
