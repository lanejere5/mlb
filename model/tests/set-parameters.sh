#!/bin/sh

# initialize model parameters
# for testing purposes

# note that there are two abbreviation systems,
# one from retrosheet and the other from fan-graphs.
# there are no conflicts between them, just differences.
# 'map' says how to handle both of them.

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
      "map":
        {
          "ANA": 0,
          "LAA": 0,
          "BAL": 1,
          "BOS": 2,
          "CHA": 3,
          "CHW": 3,
          "CLE": 4,
          "DET": 5,
          "HOU": 6,
          "KCA": 7,
          "KCR": 7,
          "MIN": 8,
          "NYA": 9,
          "NYY": 9,
          "OAK": 10,
          "SEA": 11,
          "TBA": 12,
          "TBR": 12,
          "TEX": 13,
          "TOR": 14,
          "ARI": 15,
          "ATL": 16,
          "CHN": 17,
          "CHC": 17,
          "CIN": 18,
          "COL": 19,
          "LAN": 20,
          "LAD": 20,
          "SDN": 21,
          "SDP": 21,
          "MIA": 22,
          "MIL": 23,
          "NYN": 24,
          "NYM": 24,
          "PHI": 25,
          "PIT": 26,
          "SFN": 27,
          "SFG": 27,
          "SLN": 28,
          "STL": 28,
          "WAS": 29,
          "WSN": 29,
          "MON": 29,
          "CAL": 0,
          "FLO": 22
        },
      "date": "2022-07-12"
    }
  }'
