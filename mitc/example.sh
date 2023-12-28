#!/usr/bin/env bash

datafile="examples/input.json"

if [ -n "$1" ];
then
  if [ -f $1 ];
  then
    datafile=$1
  else
    echo "Usage: $0 [input.json]" >&2
    exit 1
  fi
fi

payload="$(<$datafile)"
curl -X POST \
  --data-raw "$payload" \
  -H "Content-Type: application/json; charset=utf-8" \
  http://127.0.0.1:3000/determinations/eval.json
