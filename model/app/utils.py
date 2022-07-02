# utils.py
"""Utils."""
from math import exp


def sigmoid(x):
  """Numerically stable sigmoid."""
  if x >= 0:
    return 1 / (1 + exp(-x))
  else:
    return exp(x) / (1 + exp(x))