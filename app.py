from flask import Flask, render_template, request
import json
from executor import Executor
from junit import JUnitResults
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
    return render_template('details.html',
                            actual = actual,
                            expected = expected)

@app.route('/', methods=['GET'])
def root():
        junit = JUnitResults('static/test_results.xml')
        results_by_locality = {}
        localities = [ result['locality'] for result in junit.results]
        localities = list(set(localities))
        for locality in localities:
             results_by_locality[locality] = []
        for result in junit.results:
             results_by_locality[result['locality']].append(result)
        return render_template('results.html',
                               localities = results_by_locality)

if __name__=='__main__':
    app.run()