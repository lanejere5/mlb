# Forecasting model

This service forecasts wins over 500 for each team for the next few games.

## To do (for this service)
- Add code handling the http request/response data.
- Add code for loading and saving ELO model weights from a bucket.
- Improve the model and experiment with other models.

## To do (for other services)
- data-pipeline: make request to model. Add response to json output for dashboard.
- dashboard: incorporate forecast into plot.

## To do (infrastructure)
- Create new service.
- Add github action for deployment.
- Create buckets for model weights.
