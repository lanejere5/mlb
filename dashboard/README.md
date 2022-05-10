# dashboard

# local dev

This directory contains the dockerfile and source for deploying the dashboard.

To build and test locally, run the following commands within `dashboard/app` and then open `http://localhost:9090/` in browser.
```
% docker build -t dashboard:latest .
% PORT=8080 && docker run -p 9090:${PORT} -e PORT=${PORT} dashboard

```
# deployment
- Github actions will deploy the dashboard to gcloud run whenever there is a `git push` into `/dashboard/app` (pushing to other directories will not trigger a new deployment).

