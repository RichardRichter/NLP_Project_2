import nltk
text = 'Bake the chicken in the preheated oven for 15 minutes, then reduce heat to 350 degrees F (175 degrees C), and continue baking until no longer pink at the bone and the juices run clear, about 1 hour more. An instant-read thermometer inserted into the thickest part of the thigh, near the bone should read 180 degrees F (82 degrees C). Remove the chicken from the oven, cover with a doubled sheet of aluminum foil, and allow to rest in a warm area for 15 minutes before slicing.'
text = text.replace(',','')
text = text.replace('(','')
text = text.replace(')','')
text = text.replace('.','')
tokens = nltk.word_tokenize(text)
#print(tokens)
tag = nltk.pos_tag(tokens)
print(tag)
grammar = r"""
NP:{<CD>+(<NNS>|<NNP>|<NN>|<NNPS>)+(<JJ>|<JJR>|<JJS>)*}
    {<DT>?(<JJ>|<JJR>|<JJS>)*(<NN>|<NNS>)+(<JJ>|<JJR>|<JJS>)*}
VP: {(<VB>|<VBD>|<VBG>|<VBN>|<VBP>|<VBZ>)+(<NP>|<TO>|<IN>|<DT>|<RBR>)+} 
"""
cp = nltk.RegexpParser(grammar)
result = cp.parse(tag)
print(result)
result.draw()
