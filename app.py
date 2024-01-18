from flask import Flask, render_template, request
import json
from executor import Executor

import protocols

app = Flask(__name__)

@app.route('/test', methods=['GET'])
def test():
    locality = "localities/config_aa.yml"
    template = "test_templates/00001.yml"
    if request.args.get('locality') is not None:
        locality = "localities/config_" + request.args.get('locality').lower() + ".yml"
    if request.args.get('test') is not None:
        template = "test_templates/" + request.args.get('test') + ".yml"

    executor = Executor(locality)
    artifacts = executor.exec(template)
    actual = artifacts["actual"]
    expected = {}
    for applicant in artifacts["expected"]:
         expected[applicant['person_id']] = applicant['is_eligible']
    return render_template('results.html',
                            actual = actual,
                            expected = expected)

@app.route('/', methods=['GET'])
def root():
        return render_template('test_results.html',
                               applicants = result["Applicants"])

if __name__=='__main__':
    app.run()