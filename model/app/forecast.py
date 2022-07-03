# forecast.py
"""Define Forecaster module."""
import numpy as np
import random
from typing import List

from model import Game
from elo import ELO


random.seed(42)

class Forecaster():
  """Forecast.

  Use a Model object + Monte Carlo simluation to forecast wins and losses
  based on the upcoming schedule.
  """
  def __init__(self, model_name: str) -> None:
    """Init."""
    if model_name == 'elo':
      self.model = ELO()

  def simulate_game(self, game: Game) -> int:
    """Simulate game by sampling Bernoulli RV.
    
    Returns:
    --------
    1 if home team wins,
    0 if visitor wins.
    """
    p = self.model.predict_proba(game)
    return int(random.uniform() <= p)

  def simulate_schedule(self, schedule: List[Game]) -> np.ndarray:
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

  def forecast(self, schedule: List[Game], n: int=1000) -> np.ndarray:
    """Simulate schedule n times.

    Returns:
    --------
    An array of game result probabilities (same order as schedule).
    """
    weights = np.copy(self.weights)
    results = np.zeros(len(schedule))

    for i in range(n):
      results += self.simulate_schedule(schedule)

      # reset model weights after simulation
      self.weights[:] = weights

    return results / n
