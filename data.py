volume_measurements = ['teaspoon', 't', 'tsp.', 'tablespoon', 'T', 'tbl.', 'tbs.', 'tbsp.', 'fluid ounce', 'fl oz', 'gill', 'cup', 'c', 'pint', 'p', 'pt', 'fl pt', 'quart', 'q', 'qt', 'fl qt', 'gallon', 'g' 'gal', 'ml', 'milliliter', 'millilitre', 'cc', 'mL', 'l', 'liter', 'litre', 'L', 'dl', 'deciliter', 'decilitre', 'dL']

mass_measurements = ['pound', 'lb', '#', 'ounce', 'oz', 'mg', 'milligram', 'milligramme', 'g', 'gram', 'gramme', 'kg', 'kilogram', 'kilogramme']

length_measurements = ['mm', 'millimeter', 'millimetre', 'cm', 'centimeter', 'cenimetre', 'm', 'meter', 'metre', 'inch', 'in', '\"']

size_measurements = ['small', 'medium', 'large', 'extra large', 'whole']

nonstandard_measurements = ['can', 'stick', 'handful', 'dash', 'to|taste']

measurements = volume_measurements + mass_measurements + length_measurements + size_measurements + nonstandard_measurements


cooking_methods = ['bake', 'fry', 'stir', 'roast', 'sautee', 'microwave', 'broil', 'poach', 'boil', 'reduce', 'add', 'combine', 'grill', 'steam', 'simmer', 'blanch', 'braise', 'mix', 'sear', 'blend', 'turn', 'brush', 'place', 'preheat', 'smoke', 'break', 'melt', 'spread', 'layer', 'roll out', 'peel', 'cut', 'chop', 'pinch', 'pour', 'weigh', 'measure', 'knead', 'quarter', 'cube', 'slice', 'carve', 'grate', 'squeeze', 'sprinkle']


tools = ['baking pan','baking sheet','barbecue grill','baster','basting brush','blender','bread basket','bread knife','Bundt pan','butcher block','cake pan','can opener','carafe','casserole pan','charcoal grill','cheese cloth','coffee maker','coffee pot','colander','convection oven','cookbook','cookie cutter','cookie press','cookie sheet','cooling rack','corer','crepe pan','crock','crock pot','cupcake pan','custard cup','cutlery','cutting board','Dutch oven','egg beater','egg poacher','egg timer','espresso machine','fondue pot','food processor','fork','frying pan','garlic press','gelatin mold','grater','griddle','grill pan','grinder','hamburger press','hand mixer','honey pot','ice bucket','ice cream scoop','icing spatula','infuser','jar opener','jellyroll pan','juicer','kettle','knife','ladle','lasagne pan','lid','mandolin','measuring cup','measuring spoon','microwave oven','mixing bowl','mold','mortar and pestle','muffin pan','nut cracker','oven','oven mitts','pan','parchment paper','paring knife','pastry bag','peeler','pepper mill','percolator','pie pan','pitcher','pizza cutter','pizza stone','platter','poacher','popcorn popper','pot','pot holder','poultry shears','pressure cooker','quiche pan','raclette grill','ramekin','refrigerator','rice cooker','ricer','roaster','roasting pan','rolling pin','salad bowl','salad spinner','salt shaker','sauce pan','scissors','sharpening steel','shears','sieve','skewer','skillet','slicer','slow cooker','souffle dish','spice rack','spoon','steak knife','steamer','stockpot','stove','strainer','tablespoon','tart pan','tea infuser','teakettle','teaspoon','thermometer','toaster','toaster oven','tongs','trivet','utensils','vegetable bin','vegetable peeler','waffle iron','water filter','whisk','wok','yogurt maker','zester']

cooking_mediums = ['olive oil', 'butter', 'vegetable oil']

proteins = ['beef', 'lamb', 'veal', 'pork', 'kangaroo', 'chicken', 'turkey', 'duck', 'emu', 'goose', 'fish', 'prawn', 'crab', 'lobster', 'mussels', 'oyster', 'scallop', 'clams', 'shrimp', 'milk', 'yogurt', 'yoghurt', 'cheese', 'cottage cheese', 'bean', 'lentil', 'chickpea', 'split pea', 'tofu', 'bacon', 'egg', 'egg whites', 'yolk', 'cod', 'halibut', 'salmon', 'tilapia', 'hummus', 'pork chop', 'whey', 'protien powder', 'tenderloin', 'refried bean', 'turkey bacon']

nuts_and_seeds = ['nut', 'seed', 'pecan', 'hazelnut', 'coconut', 'almond', 'chestnut', 'macadamia', 'cashew', 'walnut', 'peanut', 'peanut butter']

vegetables = ['amaranth leaves','amaranth','arrowroot','artichoke','arugula','asparagus','avocado','bamboo shoot','bamboo','beet','belgian endive','bell pepper','bitter melon','bok choy','borage','breadfruit','broad bean','broadbean','broccoli','broccoli rabe','brussel sprout','Brussels sprouts','burdock','butternut squash','cabbage','caper','cardoon','carrot','cassava','cauliflower','celeriac','celery','celery root','chard','chayote','chickpea','chicory','chinese water chestnut','collard','common bean','corn','cowpea','crookneck','cucumber','curly endive','daikon','dandelion','dock','durian','edamame','eggplant','endive','fava bean','fennel','fiddlehead','gherkin','ginger','grapeleaves ','grean pea','green bean','green cabbage','green pepper','horseradish','husk tomato','iceberg lettuce','Indian fig','jackfruit','Jerusalem artichoke','jicama','jícama','kale','kohlrabi','lamb’s lettuce','lamb’s quarters','leek','lemongrass','lentil','lettuce','lettuce leaf','lima bean','loofah','lotus','moringa','mushroom','musk cucumber','mustard green','Napa cabbage','okra','olive','onion','orange pepper','oysterplant','parsnip','pea','peanut','pepper','plantain','potato','pumpkin','radicchio','radish','red cabbage','red onion','red pepper','red potato','romaine','romaine lettuce','rutabaga','salsify','shallot','snake gourd','snap peas','snow pea','sorrel','soybean','spaghetti squash','spinach','squash','squashblossoms ','sugar snap peas','sweet potato','sweet red pepper','swiss chard','taro','ti','tomatillo','tomato','Tossa jute','turnip','water chestnut','watercress','wax gourd','white potato','yam','yam root','yellow pepper','yellow potato','yuca root','zucchini']

fruits = ['acerola', 'west indian cherry', 'apple', 'apricots', 'avocado', 'banana', 'blackberry', 'blackcurrant', 'blueberry', 'breadfruit', 'cantaloupe', 'carambola', 'cherimoya', 'cherry', 'clementine', 'coconut', 'coconut meat', 'cranberry', 'custard-apple', 'date', 'date fruit', 'durian', 'elderberry', 'feijoa', 'fig', 'gooseberry', 'grapefruit', 'grape', 'guava', 'honeydew melon', 'melon', 'jackfruit', 'java-plum', 'plum', 'jujube fruit', 'kiwi', 'kiwifruit', 'kumquat', 'lemon', 'lime', 'lingonberry', 'longan', 'loquat', 'lychee', 'mandarin', 'mandarin orange', 'mango', 'mangosteen', 'mulberry', 'nectarine', 'olive', 'orange', 'papaya', 'passion fruit', 'peach', 'pear', 'persimmon', 'pitaya', 'dragonfruit', 'pineapple', 'pitanga', 'plantain', 'pomegranate', 'prickly pear', 'prune', 'pummelo', 'quince', 'raspberry', 'rhubarb', 'rose-apple', 'sapodilla', 'mamey sapote', 'sapote', 'soursop', 'strawberry', 'sugar-apple', 'tamarind', 'tangerine', 'watermelon']

seasonings = ['allspice','angelica','anise','asafoetida','bay leaf','basil','bergamot','black cumin','black mustard','black pepper','borage','brown mustard','burnet','caraway','cardamom','cassia','catnip','cayenne pepper','celery seed','chervil','chicory','chili pepper','chives','cicely','cilantro','cinnamon','clove','coriander','costmary','cumin','curry','dill','fennel','fenugreek','filé','ginger','grains of paradise','holy basil','horehound','horseradish','hyssop','lavender','lemon balm','lemon grass','lemon verbena','licorice','lovage','mace','marjoram', 'mustard', 'nutmeg','oregano','paprika','parsley','peppermint','poppy seed','rosemary','rue','saffron','sage','savory','sesame','sorrel','star anise','spearmint','tarragon','thyme','turmeric','vanilla','wasabi','white mustard','salt', 'pepper', 'paste', 'lemon juice', 'lime juice', 'soy sauce', 'juice', 'zest', 'garlic', 'flakes', 'syrup', 'molasses', 'balsamic', 'sugar', 'extract']

binders = ['egg', 'cracker', 'cracker crumb', 'oatmeal', 'rice', 'milk', 'evaporated milk', 'gelatin', 'guar gum', 'xanthan gum', 'psyllium husk', 'potato starch']

starches = ['ciabatta', 'whole wheat bread', 'sourdough', 'rye bread', 'pita bread', 'focaccia', 'multigrain', 'brioche', 'bread', 'waffle', 'english muffin', 'dough', 'flour', 'pasta', 'noodle', 'pastry']


ingredients_list = {
	'cooking_medium': cooking_mediums,
	'protein': proteins,
	'nuts_and_seeds': nuts_and_seeds,
	'seasoning': seasonings,
	'vegetable': vegetables,
	'binder': binders,
	'starch': starches,
	'sauce': ['sauce']
}

all_ingredients = [item for k in ingredients_list for item in ingredients_list[k]]

japanese_seasonings = ['dashi', 'soy sauce', 'sake', 'mirin', 'vinegar', 'sugar', 'salt', 'ginger', 'perilla', 'takanotsume red pepper', 'wasabi']

japanese_vegetables = ['hitashi-mono', 'wakame seaweed', 'daikon', 'carrot', 'green beans', 'wakegi scallion', 'baka-gai']

japanese_cooking_techniques = ['raw', 'grilled', 'simmered', 'boiled', 'steamed', 'deep-fried', 'dressed']

japanese_binders = ['egg', 'panko']

japanese_sweets = ['anko', 'red bean paste', 'taiyaki', 'mochi']

#please note that this binder requires all ingredients and is a good replacement for egg
cool_vegetarian_binder = ['1/2 of a medium mashed banana', '1/4 cup of applesauce', '3.5 tablespoons of gelatin blend', '1 tablespoon of ground flaxseed mixed with 3 tablespoons of warm water']


