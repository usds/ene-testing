#!/usr/bin/env bash

curl -X POST \
  --data-raw "$(cat examples/input.json)" \
  -H "Content-Type: application/json; charset=utf-8" \
  http://127.0.0.1:3000/determinations/eval.json
