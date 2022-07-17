# Math

## Logistic Regression Model




## Bayesian Logistic Regression Model with Assumed Density Filtering

Team strengths are modelled as Gaussian RVs $\theta_i \sim N( \mu_i, \sigma_i^2)$.

The likelihood the home team wins is defined the same as in the logistic regression model:

$$ p(h \mid \theta_h, \theta_v) = \sigma(a (\theta_h - \theta_v) + b).$$

Team strengths are updated after each game using Bayes theorem.
However, for this model the posterior team strengths cannot be computed exactly and are not Gaussian.
We use Assumed Density Filtering as described in [1, Section 18.5.3] to approximate the posterior team strengths by Gaussians.
More specifically, our model follows the algorithm described in [1, Section 18.5.3.2] which describes Gaussian approximate for online inference in generalized linear models in detail.

The transition probability distribution for the update step in this algorithm is given by

$$ p(\theta_{i,t} \mid \theta_{i, t-1}) = N(\theta_{i,t} \mid \theta_{i,t-1} , k)$$

where $k$ is a hyperparameter which plays a role similar to the learning rate.


## Glicko


## Model evaluation


## References

[1] Murphey. Machine Learning: a Probabilistic Perspective. 2nd Ed.
[2] 