#!/usr/bin/env python3
# -*- coding: latin-1 -*-

import discord
import sounddevice as sd

# https://github.com/UFAL-DSG/alex/blob/72fd963c16e00adea6b8fb6c45441b33fc725f3c/alex/components/hub/aio.py#L192 # search for stream. 
# https://github.com/UFAL-DSG/alex/blob/72fd963c16e00adea6b8fb6c45441b33fc725f3c/alex/components/hub/vio.py#L472 # difference get_write_available. One is for pyaudio.

# Maybe sounddevice.RawStream can be used to write/read instead of this implementation?
# FUCKING WORKS FOR PHONE2DISCORD!!!!!
class IOStream(discord.PCMAudio, discord.reader.AudioSink): # Make this IOBuffer with write() and read() with slicing-on-read methods. 
    """IOStream.. Shouuld be doable with sounddevice...
    See https://python-sounddevice.readthedocs.io/en/0.3.12/api.html#sounddevice.playrec
    """
    def __init__(self, discordListen=False, duration_ms=20):
        self.discordListen = discordListen
        self.sample_rate = 48000.0 #48 KHz
        self.sample_period_sec = 1.0/self.sample_rate
        self.num_samples = int( (duration_ms/1000.0) / self.sample_period_sec )

        self.audio_stream = sd.RawStream( # This will not work properly. Reason it worked is because of computer speakers and mic probably.. Use buffer instead. 
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


    # https://gist.github.com/Apfelin/c9cbb7988a9d8e55d77b06473b72dd57
    def freshen(self, idx):
		self.bytearr_buf = self.bytearr_buf[idx:]