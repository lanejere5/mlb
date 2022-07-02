# model.py
"""Define Model abstract base class and Forecast module."""
import numpy as np
import random

from typing import List
from abc import ABC, abstractmethod
from enum import Enum
from dataclasses import dataclass

random.seed(42)


@dataclass
class Game():
  """Representation of games."""
  home: str
  visitor: str


class Model(ABC):
  """Model abstract base class.

  Represents a model that predicts win probabilities
  for individual games and has an online learning
  algorithm (implemented by step).
  """
  def __init__(self):
    return

  @abstractmethod
  def predict_proba(self, game: Game) -> float:
    """Predict probability that home team wins."""
    pass

  @abstractmethod
  def step(self, game: Game, result: float) -> None:
    """Perform single step parameter update."""
    pass

  @abstractmethod
  def save_parameters(self) -> None:
    """Save model parameters."""
    pass

  def train(self, schedule: List[Game], results: List[float]) -> None:
    """Train the model with game results."""
    for game, result in zip(schedule, results):
      self.step(game, result)


class Forecast():
  """Forecast.

  Use a Model object + Monte Carlo simluation to forecast wins and losses
  based on the upcoming schedule.
  """
  def __init__(self, model: Model) -> None:
    """Init."""
    self.model = model

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
