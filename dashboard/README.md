# dashboard

This directory contains the dockerfile and source for deploying the dashboard.

To build and test locally, run the following commands within `dashboard/app`:
```
% docker build -t dashboard:latest .
% PORT=8080 && docker run -p 9090:${PORT} -e PORT=${PORT} dashboard

```
CD is implemented with github actions.