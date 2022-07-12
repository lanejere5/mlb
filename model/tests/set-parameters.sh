#!/bin/sh

# initialize model parameters
# for testing purposes

curl -X POST https://model-5odpqk6ypq-ue.a.run.app/set_parameters \
  -H "Content-Type: application/json; charset=utf-8" \
  -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
  -d '{
  "model-name":"elo",
  "params":
    {
      "k": 4,
      "a": 0.0025,
      "b": 0.15,
      "rating": [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
      "date": "2022-07-12"
    }
  }'
