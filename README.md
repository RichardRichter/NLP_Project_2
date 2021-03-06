# Natural Language Processing: Recipe Extraction and Transformations

Github link: https://github.com/RichardRichter/NLP_Project_2 

<h2>Error Read more bytes:</h2>

Sometimes, we have had an issue with using beautiful soup, where once you input a url from allrecipes.com, an error pops up saying a reading error occured:<br />
(raise IncompleteRead(data, amt-len(data))<br />
http.client.IncompleteRead: IncompleteRead(339382 bytes read, 57603 more expected). <br />
We have found that by simply running the code again with the same url the code works as its supposed to. So if you come up with that error, just run the code again. 


<h2>How to run our project:</h2>

run python recipe.py

You will be asked to provide a url from allrecipes.com, once you enter the recipe a drop down menu of the Title of the Recipe you uploaded, a list of tools, a list of actions and a list of main actions will appear. Then the recipes original ingredients and original steps will be printed. 

After the recipe is printed, you will be select a choice of whether to output the in-depth details of the ingredients and steps of the recipe, perform a specific transformation, or quit/terminate the program. Provide the respective number from 0-8 that matches what you want to do.

<h2>More in detail about what each option does</h2>
<h3>0. Print Parsed Ingredients and Steps from Original Recipe</h3>
  This option will print our internal representation of ingredients and steps.<br />
  An individual ingredient is represented as a dictionary with these keys:
  <ul>
  <li>name (string)</li>
  <li>type (string)</li>
  <li>quantity (float)</li>
  <li>measurement (string)</li>
  <li>descriptors(list of strings)</li>
  <li>prep(list of strings)</li>
  </ul>
  The recipe's ingredients is represented as a list of these ingredient dictionaries.<br />
  <br />
  A single step corresponds to one sentence in the original instructions of the recipe. It is represented as a Step class object with internal class variables. <br />
  The relevant internal class variables are:
  <ul>
  <li>text (string that represents the original text of the instruction)</li>
  <li>actions (list of strings for each action happening in the step)</li>
  <li>ingredients (list of strings for each ingredient in this step)</li>
  <li>tools (list of strings for each tool used in this step)</li>
  <li>new_text (string that contains the new instructions after performing a transformation, this is initalized to be same as text)<br />
  </ul>
<h3>1-8. Transform the recipe in some way</h3>
  These options will change our internal representation of the recipe to match the desired transformation and then output the changed recipe starting from the title.<br />
  After the transformed recipe is printed, there will be a section printed denoting the changes made to the recipe for the transformation.<br />
  Note that some transformations can be trivial, for example transforming a recipe that is already vegetarian to vegetarian will not do anything.<br />
 
<h2>After one transformation</h2>
  Because only one transformation is done on a recipe, you are prompted to either put in a new url for another recipe (put the same url as before if you want to perform a different transformation on the same recipe) or exit the program.
