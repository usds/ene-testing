import argparse
import math
import os
import pprint
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
		def __init__(self, base, host, key, options):
			self.base = base
			self.host = host
			self.key = key
			self.options = options
			self.cardinality = len(self.options)
			self.bits = math.ceil(math.log2(self.cardinality))
			self.mask = int(math.pow(2, self.bits)) - 1

		def select(self, i):
			if i >= self.cardinality:
				return False
			try:
				self.host[self.key] = self.options[i]
			except IndexError:
				breakpoint()
			return True

		def decode(self, code):
			i = (code >> self.base) & self.mask
			return self.select(i)

	def isfuzz(obj):
		return isinstance(obj, dict) and len(obj.keys()) == 1 and 'fuzz' in obj

	def isCondition(obj):
		return isinstance(obj, dict) and len(obj.keys()) == 1 and 'fuzz-condition' in obj

	def compile(self, obj, host=None, key=None):
		if Fuzz.isfuzz(obj):
			if host is None:
				raise ValueError("can't fuzz a root")
			lint = self.Lint(self.bits, host, key, obj['fuzz'])
			self.bits += lint.bits
			self.lints.append(lint)
		if Fuzz.isCondition(obj):
			if host is None:
				raise ValueError("can't fuzz a root")
			lint = self.Lint(self.bits, host, key, obj['fuzz-condition'])
			self.conditions.append(lint)
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
		self.conditions = []
		self.bits = 0
		self.cardinality = 1
		self.executor.template = self.executor.generator.parse_test_template(test_path)
		self.compile(self.executor.template)
		for lint in self.lints:
			self.cardinality *= lint.cardinality
		self.index_limit = math.pow(2, self.bits)
		self.first()
		self.setCondition(0)

	def setPreCondition(self):
		self.setCondition(0)

	def setPostCondition(self):
		self.setCondition(1)

	def setCondition(self, index):
		success = True
		for lint in self.conditions:
			success &= lint.select(index)
		self.generate()
		return success

	def setInstance(self, index):
		self.index = index
		success = True
		for lint in self.lints:
			success &= lint.decode(index)
		return success

	def first(self):
		self.setInstance(0)

	def next(self):
		self.index += 1
		if self.index >= self.cardinality:
			return False
		while not self.setInstance(self.index):
			self.index += 1
			if self.index >= self.index_limit:
				return False
		return True

	def randomize(self):
		while True:
			index = random.getrandbits(self.bits)
			if self.setInstance(index):
				return index

	def generate(self):
		self.executor.input = self.executor.generator.generate_test_json(self.executor.template)


if __name__ == '__main__':
	parser = argparse.ArgumentParser(
		prog='generator.py',
		description='Combine templates with a locality config and then fuzz the test data')
	parser.add_argument('-c', '--config', default='localities/config_nj.yml',
					 help='select the locality config for the run')
	parser.add_argument('-t', '--test', default=None, required=True,
					 help='the fuzz test description')
	parser.add_argument('-n', '--num', default=None,
					 help='execute N tests, if N is >+ cardinality, test all possibilities in order, otherwise test a random sample')
	parser.add_argument('-s', '--seed', default=None,
					 help='select a specific seed for repeatable runs, or omit for random seed')
	parser.add_argument('-d', '--debug',
					 action=argparse.BooleanOptionalAction,
					 help='print state and break on invalid and incorrect results')

	args = parser.parse_args()
	config_filename = args.config
	if args.test is not None:
		files = [ args.test ]
	else:
		files = [os.path.join("fuzz_templates", f) 
				 for f in os.listdir('./fuzz_templates')
				 if f.endswith('yml')]
		files.sort()

	pp = pprint.PrettyPrinter(indent=2)
	fuzz = Fuzz(config_filename)

	for test_path in files:
		template_name = os.path.basename(test_path).split('.')[0]
		print(f'Generating {template_name} for {fuzz.executor.locality}')
		fuzz.load(test_path)
		print(f'there are {fuzz.cardinality} possibilities')

		n = int(args.num) if args.num is not None else fuzz.cardinality
		n = min(n, fuzz.cardinality)
		print(f'evaluating {n} cases')

		random.seed(args.seed)

		valid = 0
		correct = 0
		for i in range(n):
			if n == fuzz.cardinality:
				candidate = i
				if i == 0:
					fuzz.first()
				else:
					fuzz.next()
			else:
				candidate = fuzz.randomize()

			# test pre-condition to determine if the template is valid
			fuzz.setPreCondition()
			artifacts = fuzz.executor.exec()
			is_valid = True
			for result in artifacts['actual']:
				is_valid = is_valid and result['is_eligible']
				if args.debug and not result['is_eligible']:
					pp.pprint(result)
					print('pre condition')
					breakpoint()

			if is_valid:
				# test post-condition to determine if the outcome is correct
				valid += 1
				fuzz.setPostCondition()
				artifacts = fuzz.executor.exec()
				is_correct = True
				expected = {}
				for expectation in artifacts['expected']:
					expected[expectation['person_id']] = expectation
				for result in artifacts['actual']:
					is_correct = is_correct and expected[result['person_id']]['is_eligible'] == result['is_eligible']
					if args.debug and expected[result['person_id']]['is_eligible'] != result['is_eligible']:
						pp.pprint(result)
						print('post condition')
						breakpoint()
				if is_correct:
					correct += 1

		print(f'out of {n} cases, {valid} had valid pre-test outcomes')
		print(f'out of {valid} cases, {correct} had correct post-test outcomes')
