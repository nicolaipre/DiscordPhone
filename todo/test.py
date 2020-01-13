
import configparser
from pprint import pprint
from Softphone.Softphone import Softphone


import os
def getConfig(file_name):
    # if os.path!== file_name: sys.exit(no config file gfound!)
    cfg = configparser.RawConfigParser()
    cfg.read(file_name)
    return dict(cfg)

a = getConfig('dp.conf')
print(a)
"""


## Main
softphone = Softphone()
softphone.set_null_sound_device()
outbound = softphone.register(server='134.209.93.86', port='13337', username='201', password='Slave12345321!@1') # Outbound

softphone.call(outbound, 'sip:004797526703@134.209.93.86:13337')
input()
softphone.end_call(outbound)
"""
