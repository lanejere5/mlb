# main.py
"""
This service does two things:

train: Use results from played games to update model weights.

forecast: generates a forecast of game results.
"""
import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify

# from model import Game
# from forecast import Forecaster
# from elo import ELO


app = Flask(__name__)

load_dotenv()

@app.route("/", methods=['GET'])
def ping():
  """Train the model.

  Expects the request body to contain two lists (in JSON format):

  games: a list of games played, where each game
    is represented as a dict with keys such as
    'home' and 'visitor'.

  results: a list of 0/1 corresponding to the outcome
    of the games.
  """
  return "hello."

@app.route("/train", methods=['POST'])
def train():
  """Train the model.

  Expects the request body to contain two lists (in JSON format):

  games: a list of games played, where each game
    is represented as a dict with keys such as
    'home' and 'visitor'.

  results: a list of 0/1 corresponding to the outcome
    of the games.
  """
  # unpack request data
  data = request.get_json()

  # initialize the model
  model_name = data['model_name']
  if model_name == 'test':
    return
  # elif data['model_name'] == 'elo':
  #   m = ELO()

  # train and save model parameters
  # m.train(
  #   [Game(**g) for g in data['games']],
  #   data['results']
  # )
  # m.save_parameters()

  return

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
