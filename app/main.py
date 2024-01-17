from flask import Flask, render_template
import json

app = Flask(__name__)

class FakeApplicant:
    def getName(self):
        return "placeholder"

class FakeApplication:
    def getApplicantByUid (self, id):
        return FakeApplicant()
    
fakeapp = FakeApplication()

@app.route('/', methods=['GET'])
def root():
    with open("static/00001_NJ_result.pp") as file:
        result = json.load(file)
        
        return render_template('results.html',
                               applicants = result["Applicants"],
                               application = fakeapp)

if __name__=='__main__':
    app.run()