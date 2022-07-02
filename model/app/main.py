# main.py
"""
This service does two things:

1. Use results from played games to update model weights.

2. Generates a forecast of wins over 500 for each team by
simulating the schedule for upcoming games.
"""
import os
from dotenv import load_dotenv
from flask import Flask, request
from model import Forecast
from elo import ELO

app = Flask(__name__)

load_dotenv()

@app.route("/", methods=['GET'])
def index():
  """Generate forecast.

  Expects the request to contain three lists:

  games: a list of games played, where each game
    is represented as a dict with keys such as
    'home' and 'visitor'.

  results: a list of 0/1 corresponding to the outcome
    of the games.

  schedule: a second list of games yet to be played,
    in chronological order.

  The response contains a list of probabilities that
  the home team won each game in the schedule.
  """
  # unpack request data
  data = request.get_json()

  # initialize the model
  model_name = os.environ.get('MODEL-NAME')
  if model_name == 'elo':
    forecasting_model = ELO()

  # train and save model parameters
  forecasting_model.train(data.games, data.results)
  forecasting_model.save_parameters()

  # generate forecast
  forecast = Forecast(forecasting_model)
  forecast.forecast(data.schedule)
 
  # package forecast and return 

  return 

if __name__ == "__main__":
  app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
