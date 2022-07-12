# main.py
"""
This service does two things:

train: Use results from played games to update model weights.

forecast: generates a forecast of game results.
"""
import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify, Response

from utils import load_parameters, save_parameters
from elo import ELO


app = Flask(__name__)

load_dotenv()

@app.route("/", methods=['GET'])
def ping():
  """For testing purposes."""
  return "hello!"

@app.route("/set_parameters", methods=['POST'])
def set_parameters():
  """Set model parameters."""
  data = request.get_json()

  model_name = data['model-name']
  params = data['params']

  env_param_name = model_name.upper() + "-BUCKET-NAME"
  bucket_name = os.getenv(env_param_name)
  if bucket_name:
    save_parameters(bucket_name, params)
    return Response("Success!", status=201, mimetype='text/plain')

  return Response("Invalid model name.", status=400, mimetype='text/plain')


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

  if model_name == 'test':
    return Response("Hello!", status=201, mimetype='text/plain')

  elif model_name.upper() == 'ELO':
    bucket_name = os.getenv("ELO-BUCKET-NAME")
    params = load_parameters(bucket_name)
    m = ELO(params)

  else:
    return Response("Invalid model name", status=400, mimetype='text/plain')

  # train model and save new parameters
  m.train(data['games'], data['results'])
  save_parameters(bucket_name, m.params)

  return Response("Success!", status=201, mimetype='text/plain')

@app.route("/forecast", methods=['POST'])
def forecast():
  """Generate forecast.

  Expects the request to contain one list:

  schedule: a list of games yet to be played,
    in chronological order, where each game
    is represented as a dict with keys such as
    'home' and 'visitor'.

  The response contains a list of probabilities that
  the home team won each game in the schedule. The
  order of the probabilities is the same as the order
  of the schedule.
  """
  # unpack request data
  data = request.get_json()

  # generate forecast
  # forecaster = Forecaster(os.environ.get('MODEL-NAME'))
  # f = forecaster.forecast(
  #   [Game(**g) for g in data['schedule']]
  # )
 
  # package forecast and return 
  # return jsonify({'forecast': f})

  return data

if __name__ == "__main__":
  app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
