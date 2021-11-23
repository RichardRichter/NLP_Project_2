from bs4 import BeautifulSoup as bs
from urllib import request
from functools import lru_cache
from transformers import pipeline
import data
import requests
import unicodedata
import re
import spacy
import copy

# Loading spacy
nlp = spacy.load("en_core_web_sm")

# Query and Generation pipelines
query = pipeline('question-answering')


# Class representing a recipe
class Recipe:
	# Class representing a node in a step graph
	class Step:

		def __init__(self, sentence=None):
			if sentence is None:
				self.text = ''
				self.actions, self.ingredients, self.tools = [], [], []
				self.new_text = ''
				self.conditions = None
			else:
				self.text = ' '.join([self.convert_fraction(x) for x in sentence.split()])
				self.tokens = nlp(sentence)
				self.actions, self.ingredients, self.tools, self.valid = self.get_info()
				self.new_text = ' '.join([self.convert_fraction(x) for x in sentence.split()])
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
				qdict = {
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
		
		def convert_fraction(self, word):
			if self.is_vulgar_fraction(word[-1]):
		
				number = unicodedata.numeric(word[-1])
				if len(word) > 1:
					if word[:-2].isnumeric():
						number += float(word[:-2])
					else:
						return word
		
				return str(int(number)) if number%1==0 else str(round(float(number), 2))
		
			elif re.match(r'[0-9]+/[0-9]+', word):
				word = word.split('/')
				return str(round(float(word[0]) / float(word[1]), 2))
		
			return word
		
		def is_vulgar_fraction(self, character):
			try:
				unicodedata.numeric(character)
				try:
					float(character)
					return False
				except ValueError:
					return True
			except ValueError:
				return False

	def __init__(self, url):
		html_doc = request.urlopen(url)
		self.soup = bs(html_doc, 'html.parser')
		# recipe name
		title = self.soup.find('title')
		if ' | Allrecipes' in title.text:
			title = title.text[:-13]
		self.recipe_name = title
		self.ingredients, self.unknown, self.ingredient_indices = self.get_ingredients()
		self.text = [div.text for div in self.soup.find_all('div', {'class': 'paragraph'})]
		self.steps = self.get_steps()
		self.tools = self.named_tools()
		self.potential_main_actions = self.pmActions()
		self.main_actions = self.mActions()
		# check categories of recipe
		self.isVegetarian = False
		self.isMexican = False
		self.isDessert = False
		self.isSandwich = False
		self.changes = []
		self.tags = self.find_tags()
		span_headers = self.soup.find_all('span', {'class': 'breadcrumbs__title'})
		for title in span_headers:
			if 'sandwich' in title.text.lower():
				self.isSandwich = True
			if 'desserts' in title.text.lower():
				self.isDessert = True
			if 'mexican' in title.text.lower():
				self.isMexican = True
			if 'vegetarian' in title.text.lower():
				self.isVegetarian = True
		for item in self.tags:
			if 'sandwich' in item:
				self.isSandwich = True
			if 'desserts' in item:
				self.isDessert = True
			if 'mexican' in item:
				self.isMexican = True
			if 'vegetarian' in item:
				self.isVegetarian = True

	def find_tags(self):
		find_tag_list = self.soup.find('script', id='karma-loader')
		find_tag_list = str(find_tag_list).split()
		append_to_list = False
		tags = []
		for item in find_tag_list:
		    item = item.replace('"','')
		    item = item.replace(',','')
		    if append_to_list and '[' not in item:  
		        if ']' in item:
		            break
		        tags.append(item)
		    if 'tags:' == item:
		        append_to_list = True
		return tags
	#Identifies Potential Main Actions:
	def pmActions(self):
		first_words = []
		potential_main_actions = []
		for step in self.steps:
			each_step = step.text.split()
			first_words.append(each_step[0])
		for word in first_words:
			if word.lower() in data.cooking_methods:
				potential_main_actions.append(word)
		pma = []
		for i in potential_main_actions:
			if i.lower() not in pma:
				pma.append(i.lower())
		return pma
	#Identifies Likely main actions
	def mActions(self):
		action_list = ['cook', 'bake', 'fry', 'roast', 'grill', 'steam', 'poach', 'simmer', 'broil', 'blanch', 'braise', 'stew']
		main_actions = []
		for action in self.potential_main_actions:
			if action.lower() in action_list:
				main_actions.append(action)
		ma = []
		for i in main_actions:
			if i.lower() not in ma:
				ma.append(i.lower())
		return ma
	def named_tools(self):
		tools = []
		for step in self.steps:
			for tool in data.tools:
				if tool in step.text:
					tools.append(tool)
		t = []
		for i in tools:
			if i.lower() not in t:
				t.append(i.lower())
		return t

	def update_ingredient_indices(self):
		self.ingredient_indices = {}
		for i in range(len(self.ingredients)):
			ing = self.ingredients[i]
			self.ingredient_indices[ing['name']] = i

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
			substeps = step.text.split('.')
			for j, substep in enumerate(substeps):
				phrases = self.clean_split(substep, [',', ';', 'until', ', and'])
				for word in to_clean:
					phrases = [phrase for phrase in phrases if word not in phrase]
				substeps[j] = ', '.join(phrases)
				if 'should read' in substeps[j] and 'degree' in substeps[j] and 'thermometer' not in substeps[j]:
					substeps[j] = ''

			step = '. '.join(substeps)
			if len(step.strip()) == 0:
				self.steps[i].new_text = ''
			else:
				cleaned.append(step)
				self.steps[i].new_text = step
		self.steps = [s for s in self.steps if s.new_text != '']
		return cleaned

	def get_ingredients(self):

		# Getting all span texts with ingredients-item-name
		ingredient_strings = self.soup.find_all('span', {'class': 'ingredients-item-name'})
		ingredient_strings = [span.text.lower() for span in ingredient_strings]

		# Cleaning the ingredients
		ingredients = []
		unknown = {}
		ingredient_indices = {}
		index = 0
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
			ingredients.append(self.validate(ingredient))
			ingredient_indices[ingredient['name']] = index
			index += 1

		return ingredients, unknown, ingredient_indices


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
			name = ingredient['measurement'] + ' ' + str(ingredient['name'])
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

	# Changes recipe to be vegetarian, if it already isn't
	def to_vegetarian(self):
		if self.isVegetarian:
			new_change = "No change was made because recipe is already vegetarian"
			self.changes.append(new_change)
		else:
			meats_found = []
			for ing, ind in self.ingredient_indices.items():
				if self.ingredients[ind]['type'] == 'protein':
					for meat in data.meat_proteins:
						if meat in ing.lower() and 'broth' not in ing.lower():
							ingredient = copy.deepcopy(self.ingredients[ind])
							# whole chicken or measurement not in mass, so change unit of measurement to mass
							if ingredient['measurement'] not in data.mass_measurements:
								if 'tofu' in self.ingredient_indices:
									# add 12 ounces to already existing tofu
									tofu_index = self.ingredient_indices['tofu']
									if self.ingredients[tofu_index]['measurement'] == 'oz' or self.ingredients[tofu_index]['measurement'] == 'ounce':
										self.ingredients[tofu_index]['quantity'] += 12
									else:
										# otherwise tofu is likely in weight measurements, just double quantity
										self.ingredients[tofu_index]['quantity'] *= 2.0
									# remove the meat from ingredients and reupdate the indices
									# del self.ingredients[ind]
									self.update_ingredient_indices()
								else:
									# tofu doesn't exist so substitute it's position in the ingredients
									self.ingredients[ind] = {
										'name': 'tofu',
										'type': 'protein',
										'quantity': 12.0,
										'measurement': 'ounce',
										'descriptors': [],
										'prep': []
									}
							# the meat is weight-based so just convert the same weight in tofu
							else:
								if 'tofu' in self.ingredient_indices:
									tofu_index = self.ingredient_indices['tofu']
									if self.ingredients[tofu_index]['measurement'] == ingredient['measurement']:
										# add same quantity
										self.ingredients[tofu_index]['quantity'] += ingredient['quantity']
									else:
										# otherwise tofu is likely in another weight
										self.ingredients[tofu_index]['quantity'] += 12.0
								else:
									self.ingredients[ind] = {
																'name': 'tofu',
																'type': 'protein',
																'quantity': ingredient['quantity'],
																'measurement': ingredient['measurement'],
																'descriptors': [],
																'prep': []
															}
							meats_found.append(ingredient)
							self.update_ingredient_indices()
							# found the matched meat so stop
							break
						# case for meat broths
						elif meat in ing.lower() and 'broth' in ing.lower():
							ingredient = copy.deepcopy(self.ingredients[ind])
							self.ingredients[ind]['name'] = 'vegetable broth'
							for i, step in enumerate(self.steps):
								if ingredient['name'] in step.new_text:
									self.steps[i].new_text = self.steps[i].new_text.replace(ingredient['name'], 'vegetable broth')
							new_changes = "Replaced " + ingredient['name'] + " with vegetable broth to make recipe vegetarian"
							self.changes.append(new_changes)
							break


			# Cleaning the steps of those words
			if len(meats_found) > 0:
				steps = self.clean_substeps(data.meat_words)
				tofu_index = self.ingredient_indices['tofu']
				# Replacing meat w/ tofu
				for i, step in enumerate(self.steps):
					for meats in meats_found:
						meat_words = meats['name'].split()
						for word in meat_words:
							if word in self.steps[i].new_text:
								for k in meats:
									if k == 'name':
										self.steps[i].new_text = step.new_text.replace(word, 'tofu')
									else:
										self.steps[i].new_text = step.new_text.replace(str(meats[k]), str(self.ingredients[tofu_index][k]))
								self.steps[i].new_text = re.sub(r'(tofu )\1+', r'\1', self.steps[i].new_text)
								self.steps[i].new_text = self.steps[i].new_text.replace('tofu, tofu', 'tofu')
								self.steps[i].new_text = self.steps[i].new_text.replace('tofu, and tofu', 'tofu')
								self.steps[i].new_text = self.steps[i].new_text.replace('tofu tofu', 'tofu')

				self.isVegetarian = True
				self.recipe_name = "Vegetarian Variant of " + self.recipe_name
				self.ingredients = [i for i in self.ingredients if i not in meats_found]
				for meats in meats_found:
					new_change = "Replaced " + meats['name'] + " with tofu to make recipe vegetarian"
					self.changes.append(new_change)
			else:
				self.isVegetarian = True
				# self.changes will be empty only if no meat broths were found and replaced with vegetable broth
				if len(self.changes) == 0:
					new_change = "Couldn't find any meats in the ingredients. The recipe has now been labeled vegetarian and no changes have been made"
					self.changes.append(new_change)

	# Changes recipe to be non-vegetarian, if it already isn't
	def from_vegetarian(self):
		meats_found = []
		for ing, ind in self.ingredient_indices.items():
			if self.ingredients[ind]['type'] == 'protein':
				for meat in data.meat_proteins:
					if meat in ing:
						meats_found.append(self.ingredients[ind])
		# Sometimes the site's metadeta doesn't have the vegetarian tag, so we have to manually check for meats
		if len(meats_found) == 0:
			self.isVegetarian = True
		if not self.isVegetarian:
			new_change = "No change was made because recipe is already non-vegetarian"
			self.changes.append(new_change)
		else:
			self.ingredients.append({'name': 'vegetable oil (for chicken)',
									 'type': 'cooking medium',
									 'quantity': 1,
									 'measurement': 'tablespoon',
									 'descriptors': [],
									 'prep': []
									 })

			self.ingredients.append({'name': 'ground chicken',
									 'type': 'protein',
									 'quantity': 16,
									 'measurement': 'ounce',
									 'descriptors': [],
									 'prep': []
									 })
			self.update_ingredient_indices()
			new_step = self.Step()
			new_step.text = new_step.new_text = 'Coat a pan with thin layer of vegetable oil (for chicken), place ground chicken onto pan and cook on stove over medium heat for 7 minutes or until brown.'
			new_step.actions = ['Cook']
			new_step.ingredients = ['vegetable oil (for chicken)', 'ground chicken']
			new_step.tools = ['pan']
			self.steps.append(new_step)
			self.isVegetarian = False
			new_change = "Added ground chicken to the recipe to make it non-vegetarian."
			self.recipe_name = self.recipe_name + "With A Side Of Ground Chicken"
			self.changes.append(new_change)

	# Make recipe more healthy, currently done by halving quantities of all seasoning
	def more_healthy(self):
		for ing in self.ingredients:
			if ing['type'] == 'seasoning':
				if 'sugar' in ing['name']:
					old_sugar = ing['name']
					new_change = "Substituted " + old_sugar + " with granulated honey to make recipe more healthy"
					self.changes.append(new_change)
					ing['name'] = 'granulated honey'
					ing['descriptors'] = []
					for i, step in enumerate(self.steps):
						self.steps[i].new_text = self.steps[i].new_text.replace(old_sugar, 'granulated honey')
						self.steps[i].new_text = self.steps[i].new_text.replace('sugar', 'honey')
				elif ing['quantity'] == 0.0:
					continue
				else:
					ing['quantity'] = ing['quantity'] * 0.5
					new_change = "Halved the quantity of " + ing['name'] + " to make recipe more healthy"
					self.changes.append(new_change)
		if len(self.changes) == 0:
			print("There's no seasonings in the recipe, so it's quite healthy already. Let's add some healthier things.")
			if self.isDessert:
				new_change = "Added Banana Slices"
				self.changes.append(new_change)
				self.ingredients.append(data.banana[0])
				self.steps.append(str(data.banana_step[0]))
			else:
				new_change = "Added Avocado Slices"
				self.changes.append(new_change)
				self.ingredients.append(data.avocado[0])
				self.steps.append(str(data.avocado_step[0]))

	# Make recipe less healthy, currently done by doubling quantities of all seasoning
	def less_healthy(self):
		# basic: double all quantities of seasoning
		for ing in self.ingredients:
			if ing['type'] == 'seasoning':
				if ing['quantity'] == 0.0:
					continue
				else:
					ing['quantity'] = ing['quantity'] * 2.0
					new_change = "Doubled the quantity of " + ing['name'] + " to make recipe less healthy"
					self.changes.append(new_change)
			if ing['type'] == 'protein':
				if ing['name'] in data.lean_proteins:
					old = ing['name']
					ing['name'] = 'beef'
					for i, step in enumerate(self.steps):
						if old in step.text:
							self.steps[i].new_text = self.steps[i].new_text.replace(old, 'beef')
					new_change = "Changed " + old + " to beef, that lean protein had to go!"
					self.changes.append(new_change)
			if ing['name'] in data.fats:
				if ing['quantity'] == 0.0:
					continue
				else:
					ing['quantity'] = ing['quantity'] * 2.0
					new_change = "Doubled the quantity of " + ing['name'] + " to make recipe less healthy"
					self.changes.append(new_change)
		if len(self.changes) == 0:
			print("Recipe was already pretty unhealthy, but hey lets still make it more unhealthy")
			if self.isDessert:
				new_change = "Added Marshmellows"
				self.changes.append(new_change)
				self.ingredients.append(data.marshmellow[0])
				self.steps.append(str(data.marshmellow_step[0]))
			else:
				new_change = "Added Crispy Fried Onions"
				self.changes.append(new_change)
				self.ingredients.append(data.fried_onions[0])
				self.steps.append(str(data.fried_onions_step[0]))

	def toDouble(self):
		self.recipe_name = "Doubled " + self.recipe_name
		find_serving = self.soup.find('div', class_='recipe-adjust-servings__original-serving')
		serving = find_serving.text
		print(serving)
		serving_number = int(re.sub("[^0-9]", "", str(serving)))
		double_serving = int(serving_number * 2)
		serving = serving.replace(str(serving_number), str(double_serving))
		serving = serving.replace("Original", "Doubled")
		print(serving)
		pattern_s = re.compile(r'\d+ second')
		pattern_m = re.compile(r'\d+ minute')
		pattern_h = re.compile(r'\d+ hour')
		list_of_patterns = [pattern_s, pattern_m, pattern_h]
		for ingredient in self.ingredients:
			for y in range(0, len(self.steps)):
				name_split = ingredient['name'].split()
				for name in name_split:
					if name in self.steps[y].new_text:
						re1 = str(ingredient['quantity']) + " " + ingredient['measurement'] + " " + name
						double = ingredient['quantity'] * 2
						new_value = str(double) + " " + str(ingredient['measurement']) + " " + str(name)
						self.steps[y].new_text = re.sub(re1, new_value, self.steps[y].new_text)
				# self.steps[y].text = self.steps[y].text.replace(str(int(ingredient['quantity'])), str(double))
		for y in range(0, len(self.steps)):
			for pattern in list_of_patterns:
				if pattern.search(self.steps[y].new_text):
					values_to_change = re.findall(pattern, self.steps[y].new_text)
					for x in range(0, len(list(values_to_change))):
						replace_value = int(re.sub("[^0-9]", "", values_to_change[x]))
						greater_value = int(replace_value * 1.5)
						self.steps[y].new_text = self.steps[y].new_text.replace(str(replace_value), str(greater_value))
		self.steps.append("Repeat Steps 1-" + str(len(self.steps)) + " as you see fit")
		for x in range(0, len(self.ingredients)):
			new_change = "Doubled the amount of " + self.ingredients[x]['name']
			self.changes.append(new_change)
			initial = self.ingredients[x]['quantity']
			double = initial * 2
			self.ingredients[x]['quantity'] = double
		new_change = "All cooking times have been multiplied by 1.5"
		self.changes.append(new_change)

	def toHalf(self):
		self.recipe_name = "Halved " + self.recipe_name
		find_serving = self.soup.find('div', class_='recipe-adjust-servings__original-serving')
		serving = find_serving.text
		print(serving)
		serving_number = int(re.sub("[^0-9]", "", str(serving)))
		half_serving = serving_number / 2
		serving = serving.replace(str(serving_number), str(half_serving))
		serving = serving.replace("Original", "Halved")
		print(serving)
		pattern_s = re.compile(r'\d+ second')
		pattern_m = re.compile(r'\d+ minute')
		pattern_h = re.compile(r'\d+ hour')
		list_of_patterns = [pattern_s, pattern_m, pattern_h]
		for ingredient in self.ingredients:
			for y in range(0, len(self.steps)):
				name_split = ingredient['name'].split()
				for name in name_split:
					if name in self.steps[y].new_text:
						re1 = str(ingredient['quantity']) + " " + ingredient['measurement'] + " " + name
						half = ingredient['quantity'] / 2
						new_value = str(half) + " " + str(ingredient['measurement']) + " " + str(name)
						self.steps[y].new_text = re.sub(re1, new_value, self.steps[y].new_text)
		for y in range(0, len(self.steps)):
			for pattern in list_of_patterns:
				if pattern.search(self.steps[y].new_text):
					values_to_change = re.findall(pattern, self.steps[y].new_text)
					for x in range(0, len(list(values_to_change))):
						replace_value = int(re.sub("[^0-9]", "", values_to_change[x]))
						lesser_value = int(replace_value / 1.5)
						self.steps[y].new_text = self.steps[y].new_text.replace(str(replace_value), str(lesser_value))
		for x in range(0, len(self.ingredients)):
			new_change = "Halved the amount of " + self.ingredients[x]['name']
			self.changes.append(new_change)
			initial = self.ingredients[x]['quantity']
			half = initial / 2
			self.ingredients[x]['quantity'] = half
		new_change = "All cooking times have been divided by 1.5"
		self.changes.append(new_change)

	def toMexican(self):
		if self.isMexican == True:
			print("Hey, Wow, Looking at the meta data (and the title) it seems like this recipe is already Mexican")
			print("perhaps you would like to try a different one of our recipe conversions, I hear they are swell.")
		else:
			self.isMexican = True
			self.recipe_name = "Mexican Interpretation of: " + self.recipe_name

			ingredients = self.get_ingredients()
			list_of_altered_ingredients = []
			list_of_seasonings = []
			list_of_starches = []
			list_of_proteins = []
			list_of_sauces = []
			list_of_cheeses = []
			list_of_milks = []
			list_of_fruits = []

			# Identify things of interest
			for diction in self.ingredients:
				if diction['type'] == 'protein':
					list_of_proteins.append(self.ingredients.index(diction))
				if diction['type'] == 'seasoning':
					list_of_seasonings.append(self.ingredients.index(diction))
				if diction['type'] == 'starch':
					list_of_starches.append(self.ingredients.index(diction))
				if diction['type'] == 'sauce':
					list_of_sauces.append(self.ingredients.index(diction))
				if diction['type'] == 'fruit':
					list_of_fruits.append(self.ingredients.index(diction))

			if self.isDessert:
				# Changing Seasonings
				mds = data.mexican_dessert_seasonings
				for m in mds:
					for seasoning in list(list_of_seasonings):
						if m['name'] in self.ingredients[seasoning]['name']:
							mds = [x for x in mds if x.get('name') != m['name']]
							list_of_seasonings.remove(seasoning)
				for i in range(0, len(list_of_seasonings)):
					if i >= len(mds):
						break
					else:
						list_of_altered_ingredients.append(tuple((self.ingredients[list_of_seasonings[i]], mds[i])))

				mfs = data.mexican_fruits
				for m in mfs:
					for fruit in list(list_of_fruits):
						if m['name'] in self.ingredients[fruit]['name']:
							mfs = [x for x in mfs if x.get('name') != m['name']]
							list_of_fruits.remove(fruit)
				for i in range(0, len(list_of_fruits)):
					if i >= len(mds):
						break
					else:
						list_of_altered_ingredients.append(tuple((self.ingredients[list_of_fruits[i]], mds[i])))
				# Replacing a milk with Tres Leches
				for protein in list_of_proteins:
					if 'milk' in self.ingredients[protein]['name']:
						list_of_milks.append(protein)
				if len(list_of_milks) > 0:
					list_of_altered_ingredients.append(
						tuple((self.ingredients[list_of_milks[0]], data.mexican_tres_leches[0])))

			else:
				# Adding Salsa if a sauce was used.
				if len(list_of_sauces) > 0:
					list_of_altered_ingredients.append(
						tuple((self.ingredients[list_of_sauces[0]], data.mexican_salsa[0])))

				# Changing Starches (Sandwich Breads to Torta) and (All other starches, make one Rice)
				if self.isSandwich:
					for star in list_of_starches:
						torta = data.mexican_bread[0]
						# if self.ingredients[star]['quantity'] != 0:
						#	torta['quantity'] = self.ingredients[star]['quantity']
						# if self.ingredients[star]['measurement'] != 'whole':
						#	torta['measurement'] = self.ingredients[star]['measurement']
						list_of_altered_ingredients.append(tuple((self.ingredients[star], torta)))
				else:
					if len(list_of_starches) > 0:
						replacement_starch = data.mexican_rice[0]
						list_of_altered_ingredients.append(
							tuple((self.ingredients[list_of_starches[0]], replacement_starch)))

				# Changing Meats and identifying cheeses
				for protein in list_of_proteins:
					if 'beef' in self.ingredients[protein]['name']:
						carne_asada = data.mexican_protein[2]
						# if self.ingredients[protein]['quantity'] != 0:
						#	carne_asada['quantity'] = self.ingredients[protein]['quantity']
						# if self.ingredients[protein]['measurement'] != 0:
						#	carne_asada['measurement'] = self.ingredients[protein]['measurement']
						list_of_altered_ingredients.append(tuple((self.ingredients[protein], carne_asada)))
					if 'pork' in self.ingredients[protein]['name']:
						alpastor = data.mexican_protein[0]
						list_of_altered_ingredients.append(tuple((self.ingredients[protein], alpastor)))
					if 'cheese' in self.ingredients[protein]['name']:
						list_of_cheeses.append(protein)

				# Changing Cheeses
				mx_cheese = data.mexican_cheese
				for mex in mx_cheese:
					for che in list(list_of_cheeses):
						if mex['name'] in self.ingredients[che]['name']:
							mx_cheese = [x for x in mx_cheese if x.get('name') != mex['name']]
							list_of_cheeses.remove(che)
				for i in range(0, len(list_of_cheeses)):
					if i >= len(mx_cheese):
						break
					else:
						list_of_altered_ingredients.append(tuple((self.ingredients[list_of_cheeses[i]], mx_cheese[i])))

				# Changing Seasonings
				mexican_seasonings = data.mexican_seasonings
				for mex in mexican_seasonings:
					for seasoning in list(list_of_seasonings):
						if mex['name'] in self.ingredients[seasoning]['name']:
							mexican_seasonings = [x for x in mexican_seasonings if x.get('name') != mex['name']]
							list_of_seasonings.remove(seasoning)
				for i in range(0, len(list_of_seasonings)):
					if i >= len(mexican_seasonings):
						break
					else:
						list_of_altered_ingredients.append(tuple((self.ingredients[list_of_seasonings[i]], mexican_seasonings[i])))
			# This will alter all the necessary ingredients in the step
			for alter in list_of_altered_ingredients:
				(old, new) = alter
				new_change = "Replaced " + old['name'] + " with " + new['name']
				self.changes.append(new_change)
				old_name = old['name']
				for ing in range(0, len(self.ingredients)):
					if self.ingredients[ing]['name'] == old_name:
						self.ingredients[ing]['name'] = new['name']
						self.ingredients[ing]['type'] = new['type']
						# These are commented out because we don't want to to change any of the quantitys or measurements
						# self.ingredients[ing]['quantity'] = new['quantity']
						# self.ingredients[ing]['measurement'] = new['measurement']
						self.ingredients[ing]['descriptors'] = new['descriptors']
						self.ingredients[ing]['prep'] = new['prep']
				for x in range(0, len(self.steps)):
					space_checker = " " + old_name.lower()
					if space_checker in self.steps[x].text.lower():
						for k in old:
							if 'name' == k:
								self.steps[x].new_text = self.steps[x].new_text.lower().replace(str(old_name), str(new['name']).upper())
							else:
								self.steps[x].new_text = self.steps[x].new_text.replace(str(old[k]), str(new[k]))
					else:
						old_name_split = old_name.split()
						for name in old_name_split:
							space_checker = " " + name
							if space_checker in self.steps[x].text.lower():
								# print("in step")
								for k in old:
									if 'name' == k:
										self.steps[x].new_text = self.steps[x].new_text.lower().replace(str(name), str(new['name']).upper())
									else:
										self.steps[x].new_text = self.steps[x].new_text.replace(str(old[k]), str(new[k]))
					for k in new:
						variable = str(new[k]).upper()
						re1 = r'(' + variable + r' )' + r'\1+'
						self.steps[x].new_text = re.sub(re1, r'\1', self.steps[x].new_text)
						self.steps[x].new_text = self.steps[x].new_text.replace(str(new[k]).upper(), str(new[k]))
						variable = str(new[k])
						re2 = r'(' + variable + r' )' + r'\1+'
						self.steps[x].new_text = re.sub(re2, r'\1', self.steps[x].new_text)
						#self.steps[x].new_text = self.steps[x].new_text.replace(str(new[k]).upper(), str(new[k]))


			# If no conversions were identified, we will simply add to the pre-existing recipe
			if len(list_of_altered_ingredients) == 0:
				print("hey, we couldn't find any specific ingredients we would want to transform")
				print("so we thought we should just add a side to your requested recipe")
				if self.isDessert:
					new_change = "Added simple Arroz Con Leche Ingredients and Steps"
					self.changes.append(new_change)
					for ing in data.mexican_acl_ing:
						self.ingredients.append(ing)
					for step in data.mexican_acl_steps:
						self.steps.append(str(step))
				else:
					new_change = "Added simple Elote Ingredients and Steps"
					self.changes.append(new_change)
					for ing in data.mexican_elote_ing:
						self.ingredients.append(ing)
					for step in data.mexican_elote_steps:
						self.steps.append(str(step))

	# Returns a step graph
	def get_steps(self):
		steps = [div.text for div in self.soup.find_all('div', {'class': 'paragraph'})]

		substeps = []
		for step in steps:
			substeps += [x.strip() for x in step.split('.')]

		steps = [self.Step(x) for x in substeps]
		steps = [s for s in steps if s.valid]

		return steps

	def output_ingredients(self):
		print("Ingredients: ")
		for info in self.ingredients:
			if info['quantity'] == 0.0:
				print(info['name'], info['measurement'])
			else:
				prep_string = ', '.join(info['prep'])
				if len(prep_string) > 0:
					prep_string = ', ' + prep_string
				descriptors_not_in_name = [d for d in info['descriptors'] if d not in info['name']]
				d = ' ' + ', '.join(descriptors_not_in_name)
				if len(d) == 1:
					d = ''
				q = info['quantity']
				if q % 1 == 0.0:
					q = str(int(q))
				else:
					q = str(q)
				m = '' if info['measurement'] == 'whole' else info['measurement']
				n = info['name']
				if len(m) == 0:
					print(q + d, n + prep_string)
				else:
					print(q + d, m, n + prep_string)

	def output_steps(self):
		print("Instructions:")
		counter = 1
		for step in self.steps:
			if isinstance(step, str):
				print(str(counter) + '. ' + step)
			else:
				print(str(counter) + '. ' + step.new_text)
			counter += 1

	def output_recipe(self):
		print(self.recipe_name)
		print('')
		self.output_ingredients()
		print('')
		self.output_steps()
		print('')

	def output_tools_and_actions(self):
		print('')
		print(self.recipe_name)
		print('')
		print("We Identifed These tools:")
		if len(self.tools) == 0:
			print("Sorry No Tools Identified")
		else:
			for tool in self.tools:
				print(tool.lower(), end=", ")
		if len(self.potential_main_actions) == 0:
			print(" ")
			print("Sorry No Potentail Main Actions Identified")
			print("Sorry No Main Actions Identified")
		else:
			print(" ")
			print("We Identified these potential main actions:")
			for pa in self.potential_main_actions:
				print(pa.lower(), end=", ")
			if len(self.main_actions) == 0:
				print(" ")
				print("Sorry from these potential actions, we did not identify the main action")
			else:
				print(" ")
				print("Here are the primary main actions we have found:")
				for ma in self.main_actions:
					print(ma.lower(), end=", ")
		print('')
		print('')
	def parsed_ing_and_steps(self):
		print('Parsed Ingredients:')
		for ing in self.ingredients:
			print(ing)
		print('')
		print('Parsed Steps:')
		for step in self.steps:
			print(step)
		print('')

# Returns a valid recipe url based on an integer input
def get_recipe_url(num=259356):
	response = requests.get(f'https://www.allrecipes.com/recipe/{num}')
	if response.status_code == 200:
		return response.url
	return get_recipe_url(259356)

def main():
	print("Welcome to Jason, Nathan, and Ricky's Recipe Parser")
	still_interested = True
	while still_interested == True:
		print("Please input the url for the allrecipes recipe to parse:")
		url = input()
		while 'allrecipes.com/recipe/' not in url:
			print("This doesn't seem to be an allrecipes.com url. Try again.")
			url = input()

		recipe = Recipe(url)
		recipe.output_tools_and_actions()
		recipe.output_recipe()
		transformation_choices = [str(i) for i in range(0, 9)]
		menu_options = "Select Desired Transformation:\n0: Print Parsed Ingredients and Steps from Original Recipe\n1: Make recipe vegetarian\n2: Make recipe non-vegetarian\n" \
					   "3: Make recipe more healthy\n4: Make recipe less healthy\n" \
					   "5: Make recipe Mexican\n6: Double quantity of recipe\n7: Half quantity of recipe\n8: Quit"
		print(menu_options)
		choice = input()
		while choice not in transformation_choices:
			print("This is an invalid transformation choice. Please choose again.")
			print(menu_options)
			choice = input()
		print()
		selected_choice = int(choice)
		if selected_choice == 0:
			recipe.parsed_ing_and_steps()
		elif selected_choice == 1:
			recipe.to_vegetarian()
		elif selected_choice == 2:
			recipe.from_vegetarian()
		elif selected_choice == 3:
			recipe.more_healthy()
		elif selected_choice == 4:
			recipe.less_healthy()
		elif selected_choice == 5:
			recipe.toMexican()
		elif selected_choice == 6:
			recipe.toDouble()
		elif selected_choice == 7:
			recipe.toHalf()
		elif selected_choice == 8:
			return

		recipe.output_recipe()
		print("Changes made to original recipe:")
		for i, change in enumerate(recipe.changes):
			print(str(i+1) + '. ' + change)

		print()
		print("Please press 1 if you have a new recipe you would like to transform")
		print("Press any other number button to end your journey")
		continue_choice = input()
		if continue_choice != str(1):
			print("Okay the process is over")
			still_interested = False


if __name__ == '__main__':
	main()
	# Some valid recipes
	# urls = [9023, 259356, 20002, 237496, 16318, 228285, 24712, 54492, 218628, 19283]
	#
	# # Printing vegetarian conversions
	# for url in urls[1:2]:
	# 	recipe = Recipe(get_recipe_url(url))
	# 	# print(recipe.vegetarian())
	# 	print(recipe.text)
	# 	recipe.output_ingredients()
	# 	recipe.output_steps()
	#
	#
	# 	recipe.to_vegetarian()
	# 	# print(recipe.recipe_name)
	# 	recipe.output_ingredients()
	# 	# for steps in recipe.steps:
	# 	# 	print(steps.new_text)
	# 	print(recipe.changes)
