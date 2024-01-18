test:
	./mitc/mitc.sh start 
	poetry run pytest -v --junitxml static/test_results.xml
	./mitc/mitc.sh stop

test_one:
	./mitc/mitc.sh start 
	poetry run pytest -v test_exec.py::TestExecutor::test_response\[localities/config_aa.yml-test_templates/00002.yml]
	./mitc/mitc.sh stop
