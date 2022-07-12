# model.py
"""Define Model abstract base class."""
from typing import List, Dict
from abc import ABC, abstractmethod


class Model(ABC):
  """Model abstract base class.

  Represents a model that predicts win probabilities
  for individual games and has an online learning
  algorithm (implemented by step).
  """
  @abstractmethod
  def predict_proba(self, game: Dict) -> float:
    """Predict probability that home team wins."""
    pass

  @abstractmethod
  def step(self, game: Dict, result: float) -> None:
    """Perform single step parameter update."""
    pass

  def train(self, schedule: List[Dict], results: List[float]) -> None:
    """Train the model with game results."""
    for game, result in zip(schedule, results):
      self.step(game, result)
