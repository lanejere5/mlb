# An interactive dashboard for the MLB postseason race

I'm a big baseball fan so I made a dashboard for visualizing the MLB postseason race.

[Click here to see it in action!](https://dashboard-5odpqk6ypq-ue.a.run.app/)

## Architecture

The dashboard is built from a combination of three google Cloud Run services.
- `dashboard` serves the frontend dashboard. It loads a json file from a storage bucket.
- `data-pipeline` scrapes game results from FanGraphs, processes the data, and updates the json file. It also calls the model API and incorporates a forecast into dashboard data. It is triggered each morning by Cloud Scheduler.
- `model` is an API for forecasting model. It has two methods: 
  - `train` updates the model using the new game results each day. 
  - `forecast` uses Monte Carlo simulation to generate a prediction for upcoming games.

## Modelling

I'm currently developing several forecasting models. See `/model` for more details. 

## DevOps

One nice feature of this project is that I learned how to use Github Actions to continuously deploy each service to Cloud Run whenever new code is pushed to the corresponding directory in the repo.  So far this has saved me a lot of time doing simple things so that I can focus on writing better code. See `.github/workflows` for the github action yaml files.
