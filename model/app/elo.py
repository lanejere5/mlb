# elo.py
"""Simple ELO model."""
import os
from typing import Dict
# from dataclasses import dataclass

from model import Model
from utils import sigmoid

# @dataclass
# class ELOParams():
#   """Parameters for the ELO model."""
#   a: float
#   k: float
#   b: float
#   rating: Dict[str, float]


class ELO(Model):
  """Simple Elo Model.

  Online logistic regression model for paired comparison of teams.

  Model Parameters:
    a: scaling factor for logistic function.
    b: y-intercept.
    ratings: array of team ratings.
    k: learning rate.
  """
  def __init__(self, params: Dict) -> None:
    self.params = params

  def predict_proba(self, game: Dict) -> float:
    """Predict probability that home team wins."""
    home = self.params['map'][game['home']]
    visitor = self.params['map'][game['visitor']]
    diff = self.params['rating'][home] - self.params['rating'][visitor]
    logit = self.params['a'] * diff
    logit += self.params['b']
    return sigmoid(logit)

  def step(self, game: Dict, result: float) -> None:
    """Perform a single step of SGD."""
    p = self.predict_proba(game)
    home = self.params['map'][game['home']]
    visitor = self.params['map'][game['visitor']]
    self.params['rating'][home] += self.params['k'] * (result - p)
    self.params['rating'][visitor] += self.params['k'] * (p - result)
