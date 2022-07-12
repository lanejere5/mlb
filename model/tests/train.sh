#!/bin/sh

curl -X POST https://model-5odpqk6ypq-ue.a.run.app/train \
  -H "Content-Type: application/json; charset=utf-8" \
  -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
  -d '{"model-name":"elo","games":[{"home":"TOR","visitor":"CHW"}],"results":[1]}'
