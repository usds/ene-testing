import argparse
import math
import os
import random

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

	def __init__(
			self,
			config_filename = "localities/config_nj.yml"):
		self.executor = Executor(config_filename)

	class Lint:
		def __init__(self, base, host, key):
			self.base = base
			self.host = host
			self.key = key
			self.options = host[key]['fuzz']
			self.cardinality = len(self.options)
			self.bits = math.ceil(math.log2(self.cardinality))
			self.mask = int(math.pow(2, self.bits)) - 1

		def select(self, i):
			if i > self.cardinality:
				breakpoint()
				return False
			self.host[self.key] = self.options[i]
			return True

		def decode(self, code):
			i = (code >> self.base) & self.mask
			return self.select(i)

	def isfuzz(obj):
		return isinstance(obj, dict) and len(obj.keys()) == 1 and 'fuzz' in obj

	def compile(self, obj, host=None, key=None):
		if Fuzz.isfuzz(obj):
			if host is None:
				raise ValueError("can't fuzz a root")
			lint = self.Lint(self.bits, host, key)
			self.bits += lint.bits
			self.lints.append(lint)
		elif isinstance(obj, dict):
			for k in obj.keys():
				self.compile(obj[k], obj, k)
		elif isinstance(obj, list):
			for item in obj:
				# no fuzz in arrays yet
				self.compile(item, None, None)
		else:
			pass

	def load(self, test_path):
		self.lints = []
		self.bits = 0
		self.cardinality = 1
		self.template = self.executor.generator.parse_test_template(test_path)
		self.compile(self.template)
		for lint in self.lints:
			lint.select(0)
			self.cardinality *= lint.cardinality
		
	def select(self, index):
		success = True
		for lint in self.lints:
			success &= lint.decode(index)
		return success

	def randomize(self):
		while True:
			index = random.getrandbits(self.bits)
			if self.select(index):
				break

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
	if args.test is not None:
		files = [ args.test ]
	else:
		files = [os.path.join("fuzz_templates", f) 
				 for f in os.listdir('./fuzz_templates')
				 if f.endswith('yml')]
		files.sort()
	print(files)

	fuzz = Fuzz(config_filename)
	for test_path in files:
		template_name = os.path.basename(test_path).split('.')[0]
		print(f'Generating {template_name} for {fuzz.executor.locality}')
		fuzz.load(test_path)
		for _ in range(1,10):
			fuzz.randomize()
			print({
				'adult' : fuzz.template['test_inputs'][0]['persons'][0]['is_pregnant'],
				'child' : fuzz.template['test_inputs'][0]['persons'][1]['lives_in_state']
				})