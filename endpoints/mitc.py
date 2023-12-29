# MITC talks to the MAGI in the Cloud API endpoint

# curl -X POST \
#  --data-raw "$payload" \
#  -H "Content-Type: application/json; charset=utf-8" \
#  

import requests

class MITC:
    def adaptor(data):
        resp = requests.post(
            'http://127.0.0.1:3000/determinations/eval.json',
            json=data,
        )
        return resp.json() if resp.text else ''