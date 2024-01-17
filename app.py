from flask import Flask, render_template
import json
from executor import Executor

import protocols

app = Flask(__name__)

@app.route('/test', methods=['GET'])
def test():
    locality = "localities/config_nj.yml"
    template = "test_templates/00001.yml"
    executor = Executor(locality)
    artifacts = executor.exec(template)
    return render_template('results.html',
                            applicants = artifacts["actual"])

@app.route('/', methods=['GET'])
def root():
        return render_template('test_results.html',
                               applicants = result["Applicants"])

if __name__=='__main__':
    app.run()