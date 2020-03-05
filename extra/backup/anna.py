
"""
DiscordPhone ~ Call phones and (spoof numbers) with your friends in Discord
Author: nicolaipre

"""

# SIP imports
import configparser
from SIPPhone import SIPPhone
from threading import Thread

# Discord imports
import discord
import asyncio
import ctypes
import ctypes.util
import sounddevice as sd

# Fix opus error
discord.opus.load_opus( ctypes.util.find_library('opus') )
discord.opus.is_loaded()


# Read SIP audio from microphone source/input
class MicrophoneAudioSource(discord.PCMAudio):
    def __init__(self, duration_ms=20):
        self.SAMP_RATE_HZ = 48000.0 #48 KHz
        self.SAMP_PERIOD_SEC = 1.0/self.SAMP_RATE_HZ
        self.NUM_SAMPLES = int((duration_ms/1000.0)/self.SAMP_PERIOD_SEC)
        self.audioStream = sd.RawInputStream(samplerate=self.SAMP_RATE_HZ, channels=2, dtype='int16', blocksize=self.NUM_SAMPLES)
        self.audioStream.start()

    def read(self):
        retVal = self.audioStream.read(self.NUM_SAMPLES)
        rawData = bytes(retVal[0])
        return rawData


# Write Discord audio to speaker sink/output
class SpeakerAudioSink(discord.reader.AudioSink):
    def __init__(self, duration_ms=20):
        self.SAMPLE_RATE_HZ = 48000.0 #48 KHz - # Samples per second
        self.SAMP_PERIOD_SEC = 1.0/self.SAMPLE_RATE_HZ # Sample interval per second?
        self.NUM_SAMPLES = int((duration_ms/1000.0)/self.SAMP_PERIOD_SEC) # Calculate total samples based on variables above
        self.audioStream = sd.RawOutputStream(samplerate=self.SAMPLE_RATE_HZ, channels=2, dtype='int16', blocksize=self.NUM_SAMPLES)
        self.audioStream.start()

    def write(self, data):
        self.audioStream.write(data.data)



# Anna..
class Anna(discord.Client):
    def __init__(self, sip_config):
        super().__init__()

        # Discord stuff
        self.voiceClient = None
        self.micAudioSource = MicrophoneAudioSource()
        self.speakerAudioSink = SpeakerAudioSink()

        self.sip_config = sip_config
        #self.softphone = None
        self.softphone = Thread(target=SIPPhone(), args=(self.sip_config,))
        self.softphone.start()

    # SIP: Initiate call
    async def call(self, phone_number, spoofed_number):
        
        if self.softphone:
            await message.channel.send("softphone is not None.")
            return
        else:
            # SIP stuff - Create an object of the SIPPhone class. This will also register with our credentials from settings.conf
            #os.system("fix number in extensions.conf")
            #os.system("service asterisk reload") # Reload asterisk config to use new spoof
            self.softphone = SIPPhone(config=self.sip_config)
            DST_SIP_URI = "sip:" + phone_number + "@134.209.93.86:13337"
            self.softphone.initiateCall(DST_SIP_URI)


    # SIP: Hangup call
    async def hangup(self):
        # 1. hangup call
        # 2. stop relaying mic and speakers
        # 3. leave voice channel
        if self.softphone:
            self.softphone.endCall() # TODO: Find out why hangup is not hung up instantly... 
        else:
            await message.channel.send("There are no active calls.")


    # SIP: Clean up sip client and softphone connections
    async def cleanup(self):
        if self.softphone:
            self.softphone.destroy() # TODO: Check if call is hung up before quitting, and make sure recording / playback is destroyed
            self.softphone = None
        else:
            await message.channel.send("There are no active calls.")



    # Capture Discord login event
    async def on_ready(self):
        print("Logged in as:", self.user.name, ":", self.user.id)
        print("Running version:", discord.__version__)












    # Process incoming commands
    async def on_message(self, message):

        # Dont listen to self.....
        if message.author == self.user:
            return False


		# Quit
        if message.content.lower().startswith("!quit"):
            if self.voiceClient:
                await self.voiceClient.disconnect()
            
            if self.softphone:
                await self.cleanup() # Clean up SIP stuff
            
            await self.logout()


		# Leave
        if message.content.lower().startswith("!leave"):
            if self.voiceClient:
                await self.voiceClient.disconnect()
            else:
                await message.channel.send("Sorry, you're not in a voice channel.")


        # Hop voice channels
        if message.content.lower().startswith("!hop"):
            if self.voiceClient:
                await self.voiceClient.move_to(message.author.voice.channel)


		# Join channel, connect to system audio, and call phone
        if message.content.lower().startswith("!join"):
            if message.author.voice is None:
                await message.channel.send("Sorry, you're not in a voice channel.")
                
            else:
                await message.channel.send("Moving to " + message.author.voice.channel.name + ", directing output to " + message.channel.name + ".")
                self.voiceClient = await message.author.voice.channel.connect()

                # Connect system mic and speakers, must be here to prevent error with RTP heap warning..?
                self.voiceClient.play(self.micAudioSource)
                self.voiceClient.listen(discord.UserFilter(self.speakerAudioSink, message.author)) # TODO: Make this listen to all users (mix)
        #endIf



        # Handle outgoing call
        if message.content.lower().startswith("!call"):
            #await self.call("004797526703", "notyet")
            await self.call("004795963801", "notyet")

        # Hangup current call
        if message.content.lower().startswith("!hangup"):
            await self.hangup()

        # Cleanup
        if message.content.lower().startswith("!cleanup"):
            await self.cleanup()

#endClass - Anna









# Main
config = configparser.RawConfigParser()
config.read('DiscordPhone.conf')
config = dict(config.items())

client = Anna(sip_config=config['ASTERISK-SIP-Outbound'])

TOKEN = config['DISCORD']['token']
client.run(TOKEN)
