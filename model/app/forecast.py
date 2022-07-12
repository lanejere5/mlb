# forecast.py
"""Define Forecaster module."""
import numpy as np
import random
from typing import List, Dict
from copy import deepcopy

from model import Model


random.seed(42)

class Forecaster():
  """Forecast.

  Use a Model object + Monte Carlo simluation to forecast wins and losses
  based on the upcoming schedule.
  """
  def __init__(self, model: Model) -> None:
    """Init."""
    self.model = model

  def simulate_game(self, game: Dict) -> int:
    """Simulate game by sampling Bernoulli RV.
    
    Returns:
    --------
    1 if home team wins,
    0 if visitor wins.
    """
    p = self.model.predict_proba(game)
    return int(random.uniform() <= p)

  def simulate_schedule(self, schedule: List[Dict]) -> np.ndarray:
    """Simulate schedule.

    Args:
    -----
    schedule: chronologically ordered list of games.

    Returns:
    --------
    An array of game results (same order as schedule).
    """
    results = []

    for game in schedule:
      result = self.simulate_game(game)
      self.model.step(game, result)
      results.append(result)

    return np.array(results)

  def forecast(self, schedule: List[Dict], n: int=1000) -> np.ndarray:
    """Simulate schedule n times.

    Returns:
    --------
    An array of game result probabilities (same order as schedule).
    """
    params = deepcopy(self.model.params)
    results = np.zeros(len(schedule))

    for i in range(n):
      results += self.simulate_schedule(schedule)
      self.model.params = deepcopy(params)

    return list(results / n)
