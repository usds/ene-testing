#!/usr/bin/env python
import argparse
import json
import pprint 
import sys

parser = argparse.ArgumentParser(prog='pprint')
parser.add_argument(
    '-f', '--file',
    type=argparse.FileType('r'),
    required=False,
    default=sys.stdin,
)
args = parser.parse_args()
blob = args.file.read()
obj = json.loads(blob)
pp = pprint.PrettyPrinter(indent=2)
pp.pprint(obj)