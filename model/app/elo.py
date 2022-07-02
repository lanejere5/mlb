# elo.py
"""Simple ELO model."""
from math import exp, log

from model import Model, Game
from utils import sigmoid


class ELO(Model):
  """Simple Elo Model.

  Logistic regression model for paired comparison
  of teams.

  Teams are effectively represented as one-hot vectors.
  The linear coefficient represents its Elo rating (up to
  scalar).

  The coefficient b represents log-odds of home advantage.

  The coefficient k is the learning rate.

  step() implements a single step of SGD.
  """
  def __init__(self):
  	super(Model, self).__init__()

    # add code to load parameters from bucket here

    self.k = 4.0 # learning rate
    self.a = log(10) / 400 # scaling coefficient
    self.b = 0.1521 # y intercept (log-odds of home advantage)
    self.ratings = {} # team ratings

  def predict_proba(self, game: Game) -> float:
    """Predict probability that home team wins."""
    logit = self.a * (self.rating[game.home] - self.rating[game.visitor]) + self.b
    return sigmoid(logit)

  def step(self, game: Game, result: float) -> None:
    """Perform a single step of SGD."""
    p = self.predict_proba(game)
    self.rating[game.home] += self.k * (result - p)
    self.rating[game.visitor] += self.k * (p - result)

  def save_parameters(self) -> None:
    """Save model parameters."""

    # add code to save to bucket here
    pass
