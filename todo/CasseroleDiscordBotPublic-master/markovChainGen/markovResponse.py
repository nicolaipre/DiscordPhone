import markovify
from posify import *

# Get raw text as string.
with open("./CDmarkovModel.json") as f:
    text = f.read()

# Build the model.
text_model = POSifiedText.from_json(text)

# Generate a sentence
#
while(True):
    inString = input(">")
    #print(text_model.make_sentence_with_start(inString, strict=False))
    print(text_model.make_short_sentence(300))