#!/usr/bin/env python3
# -*- coding: latin-1 -*-

import discord
from collections import deque
from discord.opus import Decoder, BufferedDecoder

print(Decoder.SAMPLE_SIZE)                   # num samples? # 4
print(Decoder.CHANNELS)                      # channels     # 2
print(Decoder.SAMPLE_SIZE//Decoder.CHANNELS) # sample width # 2
print(Decoder.SAMPLING_RATE)                 # sample_rate  # 48000

"""
self._file.setnchannels(Decoder.CHANNELS)
self._file.setsampwidth(Decoder.SAMPLE_SIZE//Decoder.CHANNELS)
self._file.setframerate(Decoder.SAMPLING_RATE)
"""


class AudioCB(discord.PCMAudio, discord.reader.AudioSink):

    discord_audio = bytearray()
    frames = deque() # call_audio

    # write (used for listen())
    def cb_put_frame(self, frame):
        # An audio frame arrived, it is a string (i.e. ByteArray)
        self.frames.append(frame)
        print(len(frame)) # 640
        # Return an integer; 0 means success, but this does not matter now
        print("cb_put_frame()")
        return 0

    # read (used for play())
    def cb_get_frame(self, size):
        # Audio frame wanted
        print("cb_get_frame()")
        if len(self.frames):
            frame = self.frames.popleft()
            print(len(frame)) # 640
            # Send the frame out
            return frame
        else:
            # Do not emit an audio frame
            return None


    def write(self, frame): # Make this return 20 ms of data and be 640 bytes
        pass

    def read(self, frame):  # Make this return 20 ms of data and be 640 bytes
        pass







class BufferIO(discord.PCMAudio, discord.reader.AudioSink):
    def __init__(self, duration_ms=20, sample_rate=48000.0):

        self.audio_data        = bytearray()
        self.sample_rate       = sample_rate #48000.0 # 48 KHz
        self.sample_period_sec = 1.0/self.sample_rate
        self.samples_per_frame = int( (duration_ms/1000.0) / self.sample_period_sec ) * Decoder.SAMPLE_SIZE


    def _read_and_slice(self, n):
        byte_chunk      = self.audio_data[:n] 
        self.audio_data = self.audio_data[n:]
        return bytes(byte_chunk)


    def write(self, data):
        if self.discord_listen:
            print("WRITE bytes discord:", len(data.data), "| Buffer size:", len(self.audio_data))
            self.audio_data += bytes(data.data)
        else:
            print("WRITE bytes phone..:", len(data), "| Buffer size:", len(self.audio_data))
            self.audio_data += bytes(data) # TODO: Make this use Utils.Frame() 


    def read(self):
        if len(self.audio_data) <= self.samples_per_frame:
            return False

        samples = self._read_and_slice(self.samples_per_frame)
        print("READ  bytes........:", len(samples))
        return samples
