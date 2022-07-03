# elo.py
"""Simple ELO model."""
import os
from model import Model, Game
from utils import sigmoid


class ELO(Model):
  """Simple Elo Model.

  Logistic regression model for paired comparison of teams.

  Model Parameters:
    a: scaling factor for logistic function.
    b: y-intercept.
    ratings: dict of regression coefficients (with team
      abbreviations as keys).
    k: learning rate.
  """
  def __init__(self):
    super(Model, self).__init__(os.environ.get('ELO-BUCKET-NAME'))

  def predict_proba(self, game: Game) -> float:
    """Predict probability that home team wins."""
    logit = self.a * (self.rating[game.home] - self.rating[game.visitor]) + self.b
    return sigmoid(logit)

  def step(self, game: Game, result: float) -> None:
    """Perform a single step of SGD."""
    p = self.predict_proba(game)
    self.rating[game.home] += self.k * (result - p)
    self.rating[game.visitor] += self.k * (p - result)
