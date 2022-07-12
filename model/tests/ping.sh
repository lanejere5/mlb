#!/bin/sh

curl https://model-5odpqk6ypq-ue.a.run.app/ \
  -H "Authorization: Bearer $(gcloud auth print-identity-token)" \