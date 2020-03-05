
import configparser
from SIPPhone import SIPPhone

config = configparser.RawConfigParser()
config.read('DiscordPhone.conf')
config = dict(config.items())

softphone = SIPPhone(config=config['ASTERISK-SIP-Outbound'])

print(config['ASTERISK-SIP-Outbound'])

PHONE_NUMBER = "004797526703"
DST_SIP_URI = "sip:" + PHONE_NUMBER + "@134.209.93.86:13337" # Same as in config ASTERISK-SIP-Outbound


# List all sound devices and select one we want
snd_devs = softphone.lib.enum_snd_dev()
i = 0
for snd_dev in snd_devs:
    print("%i: %s" % (i, snd_dev.name))
    i = i+1

#softphone.get_sound_devices()
#softphone.set_sound_devices(capture, playback)



#softphone.initiateCall(DST_SIP_URI)

#input() # Wait for input before call is ended
#softphone.endCall()

softphone.destroy() # TODO: Check if call is hung up before quitting.
