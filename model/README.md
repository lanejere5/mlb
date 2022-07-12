# Forecasting model(s)

This service forecasts results of upcoming games.


## To do (for other services)
- data-pipeline: make request to model. Add response to json output for dashboard.
- dashboard: incorporate forecast into plot.

# Model Descriptions

## Basic Elo model (`elo.py`)

The Elo model is essentially a logistic regression model. The output is the probability that the home team wins. In it's simplest form, the input is the data of the home team and the visiting team. Teams are represented as one-hot vectors. The relative strength of a team is given by the corresponding coefficient in the logistic regression model. I.e., the log-odds that the home team wins is roughly proportional to the difference of regression coefficients `b_home - b_visitor` ('proportional to' because the sigmoid function is scaled by a temperature parameter). 

On average, the home team in major league baseball wins about 53% of the time.  This advantage is represented by the y-intercept term in the logistic regression model. (thus, the log-odds is actually proportional to a shift of `b_home - b_visitor`).

Model parameters are updated in an online fashion via stochastic gradient descent. The learning rate is a hyperparameter.

## Adjusted Elo model (`adjusted_elo.py`)

The adjusted Elo model incorporates other contextual features that are related to the (dis)advantage of the home team. Examples of these sorts of features include:
- relative pitcher strength
- restedness
- travel distance

There is [a good writeup on 538](https://fivethirtyeight.com/features/how-our-mlb-predictions-work/) about their Elo model for predicting baseball games which mentions these features and several others.

These features are incorporated as features in the logistic regression model (whose coefficients are learned parameters). The model remains otherwise the same as basic Elo.

## Bayesian model (`bayes.py`)

