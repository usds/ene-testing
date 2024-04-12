import argparse
import os
import pprint 

import endpoints
import protocols
from executor import Executor

class Fuzz:
	"""Fuzz and execute a test template

	- Transform template to input.
	- Present input to the system under test.
	- Transform response and compare to expected output.
	- repeat for every ambiguity in the template
	"""

	def __init__(self, config_filename = "localities/config_nj.yml"):
		self.executor = Executor(config_filename)
		
	def fuzz(self, template):
		pass

if __name__ == '__main__':
	parser = argparse.ArgumentParser(
		prog='generator.py',
		description='Combine templates with a locality config and then fuzz the test data')
	parser.add_argument('-c', '--config', default='localities/config_nj.yml')
	parser.add_argument('-t', '--test', default=None)
	args = parser.parse_args()

	config_filename = args.config
	fuzz = Fuzz(config_filename)
	if args.test is not None:
		files = [ args.test ]
	else:
		files = [os.path.join("fuzz_templates", f) 
				 for f in os.listdir('./fuzz_templates')
				 if f.endswith('yml')]
		files.sort()
	print(files)
	
	pp = pprint.PrettyPrinter(indent=2)

	for test_path in files:
		template_name = os.path.basename(test_path).split('.')[0]
		print(f'Generating {template_name} for {fuzz.executor.locality}')
		test_case_template = fuzz.executor.generator.parse_test_template(test_path)
		pp.pprint(test_case_template)
		fuzz.fuzz(test_case_template)
		print(test_case_template['test_inputs'][0]['persons'][0]['is_medicare_eligible'])
