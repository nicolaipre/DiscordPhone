#!/usr/bin/env python3
# -*- coding: latin-1 -*-

import discord
import sounddevice as sd

class DiscordBuffer(discord.reader.AudioSink):
    """ An audio I/O buffer (sink AND source) for Discord
    """
    def __init__(self, duration_ms=20):
        self.audio_data = bytearray()
        self.sample_rate = 48000
        self.sample_width = 1
        self.sample_period_sec = 1.0/self.sample_rate
        self.num_samples = int((duration_ms/1000.0) / self.sample_period_sec)*2 # samples_per_frame

    def write(self, data):
        self.audio_data += data.data

    def read(self): # TODO: implement freshen (removes played samples)
        ret_val = self.audio_data.read(self.num_samples)
        raw_data = bytes(ret_val[0])
        return raw_data
    


class SoftphoneBuffer(discord.PCMAudio):
    """ An audio I/O buffer (sink AND source) for Softphone
    """
    def __init__(self, duration_ms=20):
        self.audio_data = bytearray()
        self.sample_rate = 48000
        self.sample_width = 2
        self.sample_period_sec = 1.0/self.sample_rate
        self.num_samples = int((duration_ms/1000.0) / self.sample_period_sec)

    def write(self, data):
        self.audio_data += data

    def read(self): # TODO: implement freshen (removes played samples)
        ret_val = self.audio_data.read(self.num_samples)
        raw_data = bytes(ret_val[0])
        return raw_data




 # Maybe sounddevice.RawStream can be used to write/read instead of this implementation?


# FUCKING WORKS FOR PHONE2DISCORD!!!!!
class FuckerIO: # discord.PCMAudio, discord.reader.AudioSink
    """IOStream.. Shouuld be doable with sounddevice...
    See https://python-sounddevice.readthedocs.io/en/0.3.12/api.html#sounddevice.playrec
    """
    def __init__(self, discordListen=False, duration_ms=20):
        self.discordListen = discordListen
        self.sample_rate = 48000.0 #48 KHz
        self.sample_period_sec = 1.0/self.sample_rate
        self.num_samples = int( (duration_ms/1000.0) / self.sample_period_sec )

        self.audio_stream = sd.RawStream(
            samplerate=self.sample_rate, 
            channels=1, 
            dtype='int16', #bits_per_sample ?
            blocksize=self.num_samples
        )
        self.audio_stream.start()

    # softphone.write=WORKS, voiceclient.write=WORKS
    def write(self, data):
        if self.discordListen == True:
            self.audio_stream.write(data.data) # ERROR: VoiceData' has no len(), -> Remember data.data because of discord.reader.VoiceData.data!!!!
        else: # softphoneListen:
            self.audio_stream.write(data)

    # voiceclient.play=WORKS, softphone.play=NOPPPPP
    def read(self):
        retVal = self.audio_stream.read(self.num_samples)
        rawData = bytes(retVal[0])
        return rawData # return to .play() 