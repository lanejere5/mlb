# bayesian.py
"""Bayesian Logistic Regression with Assumed Density Filtering."""
from typing import Dict

import numpy as np
from math import sqrt

from model import Model
from utils import np_sigmoid

class BayesianLogisticRegressionWithADF(Model):
  """Bayesian Logistic Regression with Assumed Density Filtering.

  See math.md for details.

  Model Parameters:
    a: scaling factor for likelihood function.
    b: adjustment factor for likelihood.
    mu: array of team ratings means.
    var: array of team rating variances.
    k: transition variance.
  """
  def __init__(self, params: Dict) -> None:
    self.params = params

  def predict_proba(self, game: Dict) -> float:
    """Predict probability that home team wins.

    Uses posterior predictive.
    """
    h = self.params['map'][game['home']]
    v = self.params['map'][game['visitor']]

    mu_h = self.params['mu'][h]
    mu_v = self.params['mu'][v]
    var_h = self.params['var'][h]
    var_v = self.params['var'][v]

    # compute mean and variance of log-odds
    s_mean = self.params['a'] * (mu_h - mu_v) + self.params['b']
    s_var = (self.params['a'] ** 2) * (var_h + var_v)

    # sample log-odds and return monte-carlo estimate of posterior predictive
    s = np.random.randn(10000) * s_var + s_mean
    likelihood = np_sigmoid(s)
    return np.mean(likelihood)

  def step(self, game: Dict, result: float) -> None:
    """Perform a single step of SGD."""
    # get indices for home and visitor
    h = self.params['map'][game['home']]
    v = self.params['map'][game['visitor']]

    # compute posterior parameters according to state transition
    # f(theta_t) = \int f(theta_t | theta_{t-1}) f(theta_{t-1}) dtheta_{t-1}
    # where f(theta_t | theta_{t-1}) = N(theta_t | theta_{t-1}, k)
    mu_h = self.params['mu'][h]
    mu_v = self.params['mu'][v]
    var_h = self.params['var'][h] + self.params['k']
    var_v = self.params['var'][v] + self.params['k']

    # compute mean and variance of log odds s for the likelihood
    s_mean = self.params['a'] * (mu_h - mu_v) + self.params['b']
    s_var = (self.params['a'] ** 2) * (var_h + var_v)

    # sample log-odds
    s = np.random.randn(10000) * s_var + s_mean

    # use monte-carlo to 
    # estimate posterior mean and variance of log-odds
    likelihood = np_sigmoid(s)
    z = np.mean(likelihood)
    post_s_mean = np.mean(s * likelihood) / z
    post_s_var = np.mean((s ** 2) * likelihood) / z - (post_s_mean ** 2)

    delta_mean = post_s_mean - s_mean
    delta_var = post_s_var - s_var

    # update model parameters
    a_h = self.params['a'] * sqrt(var_h) / s_var
    a_v = - self.params['a'] * sqrt(var_v) / s_var
    self.params['mu'][h] = mu_h + a_h * delta_mean
    self.params['mu'][v] = mu_v + a_v * delta_mean
    self.params['var'][h] = var_h + (a_h ** 2) * delta_var
    self.params['var'][v] = var_v + (a_v ** 2) * delta_var
    return
