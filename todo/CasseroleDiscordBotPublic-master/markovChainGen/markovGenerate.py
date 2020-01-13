import markovify
import re
from posify import *

# Get raw text as string.
with open("./CDmarkov.txt") as f:
    text = f.read()

# Build the model.
text_model = POSifiedText(text, state_size=4)

with open("CDmarkovModel.json", "w") as f:
    model_json = text_model.to_json()
    f.write(model_json)
