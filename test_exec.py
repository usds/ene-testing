import os
import pytest
import unittest
from executor import Executor

localities = [os.path.join("localities", f) for f in os.listdir('./localities') if f.endswith('yml')]
templates = [os.path.join("test_templates", f) for f in os.listdir('./test_templates') if f.endswith('yml')]
test_cases = [(l, t) for l in localities for t in templates]

class TestExecutor:

    @pytest.mark.parametrize("locality,template", test_cases)
    def test_response(self, locality, template):
        print (os.environ["PYTEST_CURRENT_TEST"])
        executor = Executor(locality)
        artifacts = executor.exec(template)

        assert len(artifacts['expected']) == len(artifacts['actual']), "applicants missing or inserted"
        expected = {}
        for expectation in artifacts['expected']:
            expected[expectation['person_id']] = expectation
        for result in artifacts['actual']:
            assert expected[result['person_id']]['is_eligible'] == result['is_eligible'], result['reason']