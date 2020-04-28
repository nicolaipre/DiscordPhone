#!/usr/bin/env python3
# -*- coding: latin-1 -*-

import discord
"""
from discord.opus import Decoder, BufferedDecoder

print(Decoder.SAMPLE_SIZE)                   # num samples?
print(Decoder.CHANNELS)                      # channels
print(Decoder.SAMPLE_SIZE//Decoder.CHANNELS) # sample width
print(Decoder.SAMPLING_RATE)                 # sample_rate

self._file.setnchannels(Decoder.CHANNELS)
self._file.setsampwidth(Decoder.SAMPLE_SIZE//Decoder.CHANNELS)
self._file.setframerate(Decoder.SAMPLING_RATE)
"""

class BufferIO(discord.PCMAudio, discord.reader.AudioSink):
    def __init__(self, duration_ms=20, sample_rate=48000.0, discord_listen=False):

        self.audio_data        = bytearray()
        self.sample_rate       = sample_rate #48000.0 # 48 KHz
        self.sample_period_sec = 1.0/self.sample_rate
        self.num_samples       = int( (duration_ms/1000.0) / self.sample_period_sec )
        self.discord_listen    = discord_listen


    def _read_and_slice(self, n): # Remove first n bytes from bytearray.
        byte_chunk      = self.audio_data[:n] # Get first n bytes.
        self.audio_data = self.audio_data[n:] # Remove first n bytes from bytearray, since they have been fetched.
        return byte_chunk


    def write(self, data):
        if self.discord_listen:
            print("Attempting to write data.data:", type(data.data), len(data.data))
            self.audio_data += bytes(data.data)
        else:
            print("Attempting to write data:", type(data), len(data))
            self.audio_data += bytes(data)

        print("Buffer size:", len(self.audio_data))


    def read(self):
        print("Attempting to read:", self.num_samples*8)
        samples = self._read_and_slice(self.num_samples*8)
        return bytes(samples)
