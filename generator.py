#!/usr/bin/env python
# We want to take in the config, the test case, the FPL table and
# output the test case file but with actual numbers generated
# by applying the FPL

import argparse
from datetime import datetime
from dateutil.relativedelta import relativedelta
import json
import os
import sys
import time
import yaml

import protocols

class Generator:
	config_filename = ""
	config = {}
	fpl_tables = {}

	def __init__(self, config_filename = "localities/config_aa.yml"):
		self.config_filename = config_filename
		self.config = self.open_file(config_filename)
		self.locality = self.config["locality"]
		self.format = self.config["format"]
		fpl_table_object = self.open_file("fpl_tables.yml")
		self.fpl_tables = fpl_table_object["fpl_tables"]

	def open_file(self, filename):
		with open(filename, "r") as stream:
			try:
				return yaml.safe_load(stream)
			except yaml.YAMLError as exc:
				print(exc)

	def parse_test_template(self, test_template_name):
		test_data = self.open_file(test_template_name)
		return test_data

	def generate_test_data(self, test_case):
		# Requires real number conversion:
		#   - Age -> DOB
		#   - FPL limits -> dollars

		year = datetime.now().year
		if "application_year" in test_case and test_case["application_year"] != "today" :
			year = int(test_case["application_year"])

		for household_index, household in enumerate(test_case["test_inputs"]):
			persons = household["persons"]
			household_size = len(persons)
			household["household_size"] = household_size
			household["application_year"] = year
			household["locality"] = self.locality

			year = self.config["fpl_year"]
			fpl = self.fpl_tables[year]["base"] + (household_size - 1)*(self.fpl_tables[year]["increment"])
			household["fpl"] = fpl

			for person_index, person in enumerate(persons):
				date_of_birth = datetime.now() - relativedelta(years=person["age"])
				person["dob"] = int(time.mktime(date_of_birth.timetuple())) # convert datetime to UNIX timestamp for now
				for income_index, income_item in enumerate(person["income_distribution"]):
					person["income_distribution"][income_index]["amount"] = self.dollar_amount(fpl, self.config["fpl_limits"], income_item["amount"])
				persons[person_index] = person
						
			test_case["test_inputs"][household_index] = household
		
		return test_case

	def dollar_amount(self, fpl, fpl_limits, test_amount):
		if str(test_amount).isnumeric():
			return test_amount
		
		dollar_amount = 0
		test_amount_text = ""
		test_amount_suffix = ""
		if test_amount.endswith("+"):
			test_amount_text = test_amount[:len(test_amount) - 1]
			test_amount_suffix = "+"
		elif test_amount.endswith("-"):
			test_amount_text = test_amount[:len(test_amount) - 1]
			test_amount_suffix = "-"

		match test_amount_text:
			case "zero":
				dollar_amount = 0
			case "adult_limit":
				dollar_amount = ((fpl_limits["adult_limit"]) / 100) * fpl
			case "child_limit":
				dollar_amount = ((fpl_limits["child_limit"]) / 100) * fpl

		match test_amount_suffix:
			case "+":
				return dollar_amount + 1
			case "-":
				return max(dollar_amount - 1, 0)
			case _:
				return dollar_amount

	def generate_test_json(self, test_case_template):
		data = self.generate_test_data(test_case_template)

		producer = protocols.producers[self.format]
		return producer(data)

	def generate_test_file(
			self,
			test_template_name,
			output_dir = "test_inputs",
			input_filename_suffix = "_input.json"):
		test_template = self.parse_test_template(test_template_name)
		data = self.generate_test_json(test_template)

		output_filename = output_dir + "/" + test_template_name + "_" + self.locality + input_filename_suffix
		os.makedirs(os.path.dirname(output_filename), exist_ok=True)
		with open(output_filename, "w") as output_file_data:
			json.dump(data, output_file_data)

if __name__ == '__main__':
	parser = argparse.ArgumentParser(
		prog='generator.py',
		description='Combine templates with a locality config to generate test data')
	parser.add_argument('-c', '--config', default='localities/config_nj.yml')
	parser.add_argument('-t', '--test', default=None)
	args = parser.parse_args()

	config_filename = args.config
	testGen = Generator(config_filename)
	files = [os.path.join("test_templates", f) for f in os.listdir('./test_templates') if f.endswith('yml')]
	files.sort()
	if args.test is not None:
		files = [ args.test ]
	for test_path in files:
		template_name = os.path.basename(test_path).split('.')[0]
		print(f'Generating {template_name} for {testGen.locality}')
		testGen.generate_test_file(test_path)
