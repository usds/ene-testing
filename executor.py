#!/usr/bin/env python

import os
import sys
import unittest

import endpoints
import protocols
from generator import TestGenerator

class TestExecutor(unittest.TestCase):
	"""Execute a test template

	- Transform template to input.
	- Present input to the system under test.
	- Transform response and compare to expected output.
	"""

	def __init__(self, config_filename = "config_aa.yml"):
		super(TestExecutor, self).__init__()
		self.generator = TestGenerator(config_filename)
		self.locality = self.generator.locality
		self.endpoint = self.generator.config["endpoint"]
		self.format = self.generator.config["format"]

	def test_response(self, test_template_name):
		test_case_template = self.generator.parse_test_template(test_template_name)
		input = self.generator.generate_test_json(test_template_name)
		expected = test_case_template['test_outputs']
		adaptor = endpoints.adaptor[self.endpoint]
		consumer = protocols.consumers[self.format]

		actual = consumer(adaptor(input))

		self.assertEqual(expected, actual)


if __name__ == '__main__':
	# for now assume only one cmd line parameter, the name of the config file
	config_filename = "config_nj.yml"
	if len(sys.argv) > 1:
		config_filename = str(sys.argv[1])
	executor = TestExecutor(config_filename)
	files = [f for f in os.listdir('./test_templates') if f.endswith('yml')]
	files.sort()
	for f in files:
		template_name = f.split('.')[0]
		print()
		print(f'Testing {template_name} for {executor.locality}')
		print('================================')
		try:
			executor.test_response(template_name)
			print("pass")
		except AssertionError as fail:
			print("FAIL")
			print(fail)

