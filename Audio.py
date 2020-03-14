#!/usr/bin/env python3
# -*- coding: latin-1 -*-

import discord

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



class SoftphoneBuffer():
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


