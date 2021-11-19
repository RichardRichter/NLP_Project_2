from bs4 import BeautifulSoup as bs
from urllib import request
from functools import lru_cache
from transformers import pipeline
import data
import requests
import unicodedata
import re
import spacy

# Loading spacy
nlp = spacy.load("en_core_web_sm")

# Query and Generation pipelines
query = pipeline('question-answering')

# Class representing a recipe
class Recipe():

	# Class representing a node in a step graph
	class Step():
		
		def __init__(self, sentence):
			self.text = sentence
			self.tokens = nlp(sentence)
			self.actions, self.ingredients, self.tools, self.valid = self.get_info()
			self.conditions = None

		def __str__(self):
			return f'({self.actions} the {self.ingredients} using {self.tools})'

		def __repr__(self):
			return str(self)

		# Filling step info
		def get_info(self):

			# Getting items from data, then querying for missing items
			actions, ingredients, tools = self.from_data()
			actions, ingredients, tools = self.query(actions, ingredients, tools)

			
			valid = True if (actions and (ingredients or tools)) else False

			return actions, ingredients, tools, valid

		# Grabbing potential data from hardcoded lists
		def from_data(self):
			# Getting actions
			actions = [w.text for w in self.tokens if w.lemma_ in data.cooking_methods]

			# Getting ingredients
			ingredients = [w.text for w in self.tokens if w.lemma_ in data.all_ingredients]

			# Getting tools
			tools = [w.text for w in self.tokens if w.lemma_ in data.tools]

			return actions, ingredients, tools

		# Finding more data with queries
		def query(self, actions, ingredients, tools):

			# Given a question as a string, returns an answer and a confidence in that answer
			def answer(question):
				qdict =  {
					'question': question,
					'context': self.text
				}

				return query(qdict)['answer'], query(qdict)['score']


			def append_answer(l, question, threshold=0):
				item, confidence = answer(question)
				if confidence > threshold and len(item.split()) < 4:
					l.append((item, confidence))


			# Querying actions
			if not actions:

				# Querying using ingredients
				for ingredient in ingredients:
					question = f'do what with {ingredient}?'
					append_answer(actions, question)

				# Querying using tools
				for tool in tools:
					question = f'do what with {tool}?'
					append_answer(actions, question)

			# Deleting duplicates
			actions = list(set(actions))


			# Querying ingredients
			if not ingredients:

				for action in actions:
					question = f'{action} what?'
					append_answer(ingredients, question)

			ingredients = list(set(ingredients))


			# Querying tools
			if not tools:

				for action in actions:
					for ingredient in ingredients:
						question = f'{action} {ingredient} in a what?'
						append_answer(tools, question)

			tools = list(set(tools))

			return actions, ingredients, tools


	def __init__(self, url):
		html_doc = request.urlopen(url)
		self.soup = bs(html_doc, 'html.parser')
		self.ingredients, self.unknown = self.get_ingredients()
		self.text = [div.text for div in self.soup.find_all('div', {'class':'paragraph'})]
		self.steps = self.get_steps()
		self.isVegetarian = False
		self.isMexican = False
		self.isDessert = False
		self.isSandwich = False
		span_headers = self.soup.find_all('span',{'class':'breadcrumbs__title'})
		for title in span_headers:
		    if 'sandwich' in title.text.lower():
		        self.isSandwich = True
		    if 'desserts' in title.text.lower():
		        self.isDessert = True
		    if 'mexican' in title.text.lower():
		        self.isMexican = True
		    if 'vegetarian' in title.text.lower():
		        self.isVegetarian = True
		print("Sandwich: ", self.isSandwich)
		print("Veggie: ", self.isVegetarian)
		print("Mexican: ", self.isMexican)
		print("Dessert: ", self.isDessert)


	@staticmethod
	def clean_split(string, seps):
		result = [string]
		for sep in seps:
			new = result[:]
			result = []
			for phrase in new:
				new_phrase = phrase.split(sep)
				if sep.isalpha() and len(new_phrase) > 1:
					new_phrase = [new_phrase[0]] + [sep + x for x in new_phrase[1:]]
				result += new_phrase

		if result[-1].strip() == 'or':
			result = result[:-1]
		return [x.strip() for x in result if x != ' ']


	# Given a list of words, cleans substeps of phrases that contain those words
	def clean_substeps(self, to_clean):

		# Getting substeps
		cleaned = []
		for i, step in enumerate(self.steps):
			substeps = step.split('.')
			for i, substep in enumerate(substeps):
				phrases = self.clean_split(substep, [',', ';', 'until', 'and'])
				for word in to_clean:
					phrases = [phrase for phrase in phrases if word not in phrase]
				substeps[i] = ', '.join(phrases)


			step = '. '.join(substeps)
			cleaned.append(step[:-1])

		return cleaned


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
		if ingredient['measurement'] not in data.measurements:
			name = ingredient['measurement'] +' '+ ingredient['name']
			for word in name.split():
				if word in data.measurements or word[:-1] in data.measurements:
					ingredient['measurement'] = 'to taste' if word == 'to|taste' else word
					ingredient['name'] = name.replace(word, '').replace('  ', ' ').strip()
					break
			else:
				ingredient['name'] = name
				ingredient['measurement'] = 'whole'

		# Validating ingredients, getting type information
		for ingredient_type in data.ingredients_list:
			if ingredient['name'] in data.ingredients_list[ingredient_type]:
				ingredient['type'] = ingredient_type
				break

		# Ingredient type not found, checking individual words
		else:
			for word in reversed(ingredient['name'].split()):
				found = False

				for ingredient_type in data.ingredients_list:
					ingredients = data.ingredients_list[ingredient_type]
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

	# Outputs a vegetarian-ized version of the recipe
	def vegetarian(self):

		# Words that will be used to clean substeps
		meat_words = ['bone', 'bone', 'skin', 'blood', 'juice', 'juice', 'pink', 'meat', 'cavity']

		# Cleaning the steps of those words
		steps = self.clean_substeps(meat_words)

		# Replacing chicken w/ tofu
		for i, step in enumerate(steps):
			steps[i] = step.replace('chicken', 'tofu')

		return steps

	def toMexican(self):
		return 0

	# Returns a step graph
	def get_steps(self):
		steps = [div.text for div in self.soup.find_all('div', {'class':'paragraph'})]

		substeps = []
		for step in steps:
			substeps += [x.strip() for x in step.split('.')]

		steps = [self.Step(x) for x in substeps]
		steps = [s for s in steps if s.valid]

		return steps


# Returns a valid recipe url based on an integer input
def get_recipe_url(num=259356):
	response = requests.get(f'https://www.allrecipes.com/recipe/{num}')
	if response.status_code == 200:
		return response.url
	return get_recipe_url(259356)



if __name__ == '__main__':

	# Some valid recipes
	urls = [9023, 259356, 20002, 237496, 16318, 228285]
	
	# Printing vegetarian conversions
	for url in urls[1:2]:
		recipe = Recipe(get_recipe_url(url))
		#print(recipe.vegetarian())
		print(recipe.text)
		for x in recipe.steps:
			print(x)
