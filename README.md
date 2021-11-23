# Natural Language Processing: Recipe Extraction and Transformations

<h2>Error Read more bytes:</h2>

Sometimes, we have had an issue with using beautiful soup, where once you input a url from allrecipes.com, an error pops up saying a reading error occured, (Read more bytes, etc.). We have found that by simply running the code again with the same url the code works as its supposed to. So if you come up with that error, just run the code again. 


<h2>How to run our project:</h2>

run python recipe.py

You will be asked to provide a url from allrecipes.com, once you enter the recipe a drop down menu of the Title of the Recipe you uploaded, a list of tools, a list of actions and a list of main actions will appear. Then the recipes original ingredients and original steps will be printed. 

After the recipe is printed, you will be select a choice of whether to output the in-depth details of the ingredients and steps of the recipe, perform a specific transformation, or quit/terminate the program. Provide the respective number from 0-8 that matches what you want to do.

<h3>More in detail about what each option does</h3>
<b>0. Print Parsed Ingredients and Steps from Original Recipe</b>
  This option will print our internal representation of ingredients and steps.<br />
  An individual ingredient is represented as a dictionary with these keys: name (string)<br />
                                                                           type (string)<br />
                                                                           quantity (float)<br />
                                                                           measurement (string)<br />
                                                                           descriptors(list of strings)<br />
                                                                           prep(list of strings)<br />
  The recipe's ingredients is represented as a list of these ingredient dictionaries.<br />
 
  A single step corresponds to one sentence in the original instructions of the recipe. It is represented as a Step class object with internal class variables.
  The relevant internal class variables are: text (string that represents the original text of the instruction)
                                             actions (list of strings for each action happening in the step)
                                             ingredients (list of strings for each ingredient in this step)
                                             tools (list of strings for each tool used in this step)
                                             new_text (string that contains the new instructions after performing a transformation, this is initalized to be same as text)
 <br>
<b>1-7. Transforma the recipe in some way
  These options will change our internal representation of the recipe to match the desired transformation and then output the changed recipe starting from the title. 
  After the transformed recipe is printed, there will be a section printed denoting the changes made to the recipe for the transformation. 
  Note that some transformations can be trivial, for example transforming a recipe that is already vegetarian to vegetarian will not do anything.
 
