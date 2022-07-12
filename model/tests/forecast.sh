#!/bin/sh

# test the forecast method

curl -X POST https://model-5odpqk6ypq-ue.a.run.app/forecast \
  -H "Content-Type: application/json; charset=utf-8" \
  -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
  -d '{
    "model-name":"elo",
    "schedule":[
      {
        "home":"TOR",
        "visitor":"CHW"
      },
      {
        "home":"BOS",
        "visitor":"NYY"
      },
      {
        "home":"TBR",
        "visitor":"BAL"
      },
      {
        "home":"TOR",
        "visitor":"CHW"
      },
      {
        "home":"BOS",
        "visitor":"NYY"
      },
      {
        "home":"TBR",
        "visitor":"MIA"
      },
      {
        "home":"TOR",
        "visitor":"CHW"
      },
      {
        "home":"LAD",
        "visitor":"NYM"
      },
      {
        "home":"TBR",
        "visitor":"BAL"
      }
    ]
  }'
