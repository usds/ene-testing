#!/usr/bin/env python

import argparse
import os

import endpoints
import protocols
from generator import Generator

class Executor:
	"""Execute a test template

	- Transform template to input.
	- Present input to the system under test.
	- Transform response and compare to expected output.
	"""

	def __init__(self, config_filename = "localities/config_aa.yml"):
		self.generator = Generator(config_filename)
		self.locality = self.generator.locality
		self.endpoint = self.generator.config["endpoint"]
		self.format = self.generator.config["format"]

	def exec(self, test_template_name):
		test_case_template = self.generator.parse_test_template(test_template_name)
		input = self.generator.generate_test_json(test_template_name)
		expected = test_case_template['test_outputs']
		adaptor = endpoints.adaptor[self.endpoint]
		consumer = protocols.consumers[self.format]

		return {
			'expected': expected,
			'actual': consumer(adaptor(input)),
		}


if __name__ == '__main__':
	parser = argparse.ArgumentParser(
		prog='executor.py',
		description='Execute tests against Medicaid eligibility backends')
	parser.add_argument('-c', '--config', default='localities/config_nj.yml')
	parser.add_argument('-t', '--test', default='test_templates/00001.yml')
	args = parser.parse_args()

	config_filename = args.config
	executor = Executor(config_filename)
	test_path = args.test
	template_name = os.path.basename(test_path).split('.')[0]
	print(f'Testing {template_name} for {executor.locality}')
	print('================================')
	print(executor.exec(test_path))