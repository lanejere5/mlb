# An interactive dashboard for the MLB postseason race

I'm a big baseball fan so I made a dashboard for visualizing the MLB postseason race.

[Click here to see it in action!](https://dashboard-5odpqk6ypq-ue.a.run.app/)

I had a few basic goals for this project:
- Create and deploy a live interactive dashboard. (see `/dashboard`).
- Implement a pipeline for ingesting real world data (see `/data-pipeline`).
- Learn to use github actions to deploy services on `git push` (see `.github/workflows`).

I'm currently developing forecasting models and incorperating those forecasts into the plot. The forecasting models are being deployed as an API via Cloud Run. See `/model`.
