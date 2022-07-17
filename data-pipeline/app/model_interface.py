# model_interface.py
"""Interface for the model API."""
import urllib
import json
import os
from typing import Dict, List

import google.auth.transport.requests
import google.oauth2.id_token

# endpoint = os.environ.get('MODEL-API-URL')
endpoint = 'https://model-5odpqk6ypq-ue.a.run.app'

def make_request(method: str=None, data: Dict=None):
  """Make API request.

  Args:
  -----
  method (optional): None, train', or 'forecast'.
  data (optional): request content for 'train' and 'forecast'
    methods. Must not be None if method is 'train' or 'forecast'.

  Assumes data conforms to the model API requirements.

  Returns:
  --------
  HTTPResponse.
  """
  if method is not None:
    assert method in {'train', 'forecast'}
    assert data is not None
    print(endpoint, method)
    url = os.path.join(endpoint, method)
  else:
    url = endpoint # in this case we just ping the API.

  # get id token for request
  auth_req = google.auth.transport.requests.Request()
  id_token = google.oauth2.id_token.fetch_id_token(auth_req, endpoint)

  # create request
  req = urllib.request.Request(url)
  req.add_header("Authorization", f"Bearer {id_token}")
  if method is not None:
    req.add_header("Content-Type", "application/json; charset=utf-8")
    req.data = bytes(json.dumps(data), encoding="utf-8")

  # send request  
  return urllib.request.urlopen(req)

def ping() -> None:
  """Ping the model.

  For testing purposes. Does nothing.
  """
  make_request()

def train(model_name: str, games: List[Dict], results: List[int]) -> None:
  """Train the model.

  Args:
  -----
  model_name: name of model to train.
  games: list of game dicts
  results: binary list indicating if home team won or lost
  """
  data = {
    'model-name': model_name,
    'games': games,
    'results': results
  }

  _ = make_request(method='train', data=data)

  return

def forecast(model_name: str, games: List[Dict]) -> List[float]:
  """Get model forecast.

  Args:
  -----
  model_name: name of model to generate forecast
  games: data for upcoming games.

  Returns:
  --------
  The same list of dicts with an additional field, 'win_probability'
  added to each game dict.
  """
  data = {
    'model-name': model_name,
    'schedule': games
  }

  response = make_request(method='forecast', data=data)
  data = json.loads(response.read())
  return data['forecast']
