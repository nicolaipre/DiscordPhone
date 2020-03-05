import sounddevice as sd
from pprint import pprint

all = sd.query_devices()
pprint(all)

#print("---------")

#input = sd.query_devices(kind='input')
#pprint(input)

#print("---------")
#output = sd.query_devices(kind='output')
#pprint(output)

#print("---------")

#pprint(sd.query_hostapis())

#pprint(sd.check_input_settings(device='pulse'))

#pprint(sd.check_output_settings(device='pulse'))
