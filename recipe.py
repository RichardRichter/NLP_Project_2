from bs4 import BeautifulSoup as bs
from urllib import request
from data import *
import requests
import unicodedata
import re
import spacy

# Loading spacy
nlp = spacy.load("en_core_web_sm")

# Class representing a recipe
class Recipe():

	def __init__(self, url):
		html_doc = request.urlopen(url)
		self.soup = bs(html_doc, 'html.parser')
		self.ingredients, self.unknown = self.get_ingredients()
		self.steps = [div.text for div in self.soup.find_all('div', {'class':'paragraph'})]


	def get_ingredients(self):

		# Getting all span texts with ingredients-item-name
		ingredient_strings = self.soup.find_all('span',{'class':'ingredients-item-name'})
		ingredient_strings = [span.text.lower() for span in ingredient_strings]

		# Cleaning the ingredients
		ingredients = {}
		unknown = {}
		for string in ingredient_strings:

			# Replacing thin spaces
			string = string.replace('\u2009', '')

			# Ingredient structure
			ingredient = {
							'name': '',
							'type': 'NULL',
							'quantity': .0,
							'measurement': '',
							'descriptors': [],
							'prep': []
							}

			# Very special case
			if 'to taste' in string:
				string = string.replace('to taste', 'to|taste')

			# Parsing out descriptors in parentheses
			parens = re.search(r'(\(.*\))', string)
			if parens:
				for paren in parens.groups():
					ingredient['descriptors'].append(paren[1:-1])
					string = string.replace(paren, '')
					string = string.replace('  ', ' ')

			# Determining if the ingredient has 'prep steps'
			string = string.split(',')
			if len(string) > 1:
				ingredient['prep'] = [string[1].strip()]

			# Determining if the ingredient has an explicit quantity
			string = string[0].split()
			has_quantity = False
			for i, word in enumerate(string):

				# Catching more preparatory steps
				if word.endswith('ed'):
					ingredient['prep'].append(word)
					string[i] = None

				# Replacing 'A and a' with 1
				if word.lower() == 'a':
					word = '1'
					string[i] = '1'

				# Checking for numbers
				try:
					number = self.convert_fraction(word)
					string[i] = number
					has_quantity = True
				except ValueError:
					continue

			# Removing null words that were added as prep
			string = [x for x in string if x is not None]

			# If the string has an explicit quanity
			if has_quantity:
				if len(string) == 1:
					ingredient['name'] = string[0]
				elif len(string) == 2:
					ingredient['quantity'] = string[0]
					ingredient['measurement'] = 'whole'
					ingredient['name'] = string[1]
				else:
					ingredient['quantity'] = string[0]
					ingredient['measurement'] = string[1]
					ingredient['name'] = ' '.join([str(x) for x in string[2:]])


			# Special cases where there is no quantity
			else:
				ingredient['name'] = ' '.join(string)
				unknown[ingredient['name']] = ingredient


			# After constructing the ingredient, we want to validate them before entering them into the ingredients list
			# This initial parse will properly handle most ingredients, but the validation step is necessary to improve accuracy for the others
			ingredients[ingredient['name']] = self.validate(ingredient)

		return ingredients, unknown


	# Given a vulgar fraction string, returns a float
	def convert_fraction(self, string_fraction):
		if len(string_fraction) == 1:
			return unicodedata.numeric(string_fraction)
		else:
			return sum([self.convert_fraction(c) for c in string_fraction])


	# Validates the legitimacy/accuracy of an ingredient parse, returning a modified ingredient
	def validate(self, ingredient):

		# Validating measurements
		if ingredient['measurement'] not in measurements:
			name = ingredient['measurement'] +' '+ ingredient['name']
			for word in name.split():
				if word in measurements or word[:-1] in measurements:
					ingredient['measurement'] = 'to taste' if word == 'to|taste' else word
					ingredient['name'] = name.replace(word, '').replace('  ', ' ').strip()
					break
			else:
				ingredient['name'] = name
				ingredient['measurement'] = 'whole'

		# Validating ingredients, getting type information
		for ingredient_type in ingredients_list:
			if ingredient['name'] in ingredients_list[ingredient_type]:
				ingredient['type'] = ingredient_type
				break

		# Ingredient type not found, checking individual words
		else:
			for word in reversed(ingredient['name'].split()):
				found = False

				for ingredient_type in ingredients_list:
					ingredients = ingredients_list[ingredient_type]
					if word in ingredients or word[:-1] in ingredients:
						ingredient['type'] = ingredient_type
						found = True
						break

				if found:
					break

		# Identifying 'descriptors'
		per_word = [token.text for word in ingredient['name'].split() for token in nlp(word) if token.pos_ == 'ADJ']

		per_whole = [token.text for token in nlp(ingredient['name']) if token.pos_ == 'ADJ']

		for word in ingredient['name'].split():
			if word in per_word or word in per_whole:
				ingredient['descriptors'].append(word)

		return ingredient


def get_recipe_url(num=259356):
	response = requests.get(f'https://www.allrecipes.com/recipe/{num}')
	if response.status_code == 200:
		return response.url
	return get_recipe_url(259356)


urls = [259356, 20002, 237496, 16318, 228285]

for url in urls:
	recipe = Recipe(get_recipe_url(url))
	for x in recipe.ingredients.values(): print(x)
	print()