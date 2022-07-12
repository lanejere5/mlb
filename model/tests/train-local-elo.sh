#!/bin/sh

curl -X POST localhost:9090/train \
  -H "Content-Type: application/json; charset=utf-8" \
  -d '{"model-name":"elo","games":[{"home":"TOR","visitor":"CHW"}],"results":[1]}' 
