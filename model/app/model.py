# model.py
"""Define Model abstract base class and Forecast module."""
from typing import List
from abc import ABC, abstractmethod
from dataclasses import dataclass

from utils import load_parameters, save_paramters

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
  def __init__(self, name: str) -> None:
    self.name = name
    self.params = load_parameters(self.name)

  @abstractmethod
  def predict_proba(self, game: Game) -> float:
    """Predict probability that home team wins."""
    pass

  @abstractmethod
  def step(self, game: Game, result: float) -> None:
    """Perform single step parameter update."""
    pass

  def save_parameters(self) -> None:
    """Save model parameters."""
    save_paramters(self.name, self.params)

  def train(self, schedule: List[Game], results: List[float]) -> None:
    """Train the model with game results."""
    for game, result in zip(schedule, results):
      self.step(game, result)
