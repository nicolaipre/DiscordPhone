#!/usr/bin/env python3
# -*- coding: latin-1 -*-

import discord
from collections import deque
from discord.opus import Decoder, BufferedDecoder

#print(Decoder.SAMPLE_SIZE)                   # num samples? # 4
#print(Decoder.CHANNELS)                      # channels     # 2
#print(Decoder.SAMPLE_SIZE//Decoder.CHANNELS) # sample width # 2
#print(Decoder.SAMPLING_RATE)                 # sample_rate  # 48000

#self._file.setnchannels(Decoder.CHANNELS)
#self._file.setsampwidth(Decoder.SAMPLE_SIZE//Decoder.CHANNELS)
#self._file.setframerate(Decoder.SAMPLING_RATE)


class AudioCB(discord.PCMAudio, discord.reader.AudioSink):

    def __init__(self, duration_ms=20, sample_rate=48000.0, channel_count=2):
        self.duration_ms = duration_ms
        self.sample_rate = sample_rate
        self.channel_count = channel_count

        # To get frame size (samples_per_frame)
        self.sample_period_sec = 1.0/self.sample_rate
        self.samples_per_frame = int( (duration_ms/1000.0) / self.sample_period_sec )

        self.phone_audio   = deque()
        self.discord_audio = deque()

        # For multi-user voice
        self.speakers = []
        self.tmp_audio_bytes = []





    ### phone -> discord ###

    def cb_put_frame(self, frame): # Denne er good! Testet med loopback i telefon
        """ Listen to the audio coming from phone, and write to phone_audio buffer.

            Phone: Write method
        """
        # An audio frame arrived, it is a string (i.e. ByteArray)
        self.phone_audio.append(frame)
        #print(len(frame))
        # Return an integer; 0 means success, but this does not matter now
        return 0



    # Denne er fucka...
    def read(self):
        """ Read from discord_audio buffer, and send audio to phone.

            Get an audio frame to be played into phone speaker.

            Discord: Read method
        """
        #print("jalla_enter")
        if len(self.phone_audio): # funker når vi relayer discord...
            frame = self.phone_audio.popleft()
            #print("jalla_frame")
            return bytes(frame)
        else:
            print("empty frame of null bytes RETURNED") # play stopper når det er tomt for frames.
            return b'\x00' * self.samples_per_frame  # Return an empty frame of null bytes








    ### discord -> phone ### (denne er good = de to under er good...)

    def write(self, voiceData): # Make this return 20 ms of data and be 640 bytes
        """ Listen to the audio coming from Discord, and write to discord_audio buffer.

            Discord: Write method
        """

        #print(f"{voiceData.user}\t- FrameBytes: {[n for n in voiceData.data[:30]]}")
        #self.discord_audio.append(voiceData.data) # appends a frame of voice data

        speaker_id = voiceData.user.id

        if speaker_id in self.speakers:
            # amount of speakers is len(self.speakers)
            speakerAmount = len(self.tmp_audio_bytes)
            frame = [0] * 3840
            
            for speaker_cnt, data in enumerate(self.tmp_audio_bytes):
                for i in range(speaker_cnt, len(data)-speakerAmount, speakerAmount):
                    frame[i] = data[i]

            #print(f"       Prev. FrameBytes: {frame[:30]}")
            #print("---------------")
            self.discord_audio.append(bytes(frame)) # Must be 3840 bytes

            self.speakers = []
            self.tmp_audio_bytes = []

        #if voiceData.data != b"\x00"*3840:
        self.tmp_audio_bytes.append(voiceData.data)
        self.speakers.append(speaker_id)


    def cb_get_frame(self, size): # Denne er good! Testet med loopback i telefon
        """ Read from discord_audio buffer, and send audio to phone.

            Get an audio frame to be played into phone speaker.

            Phone: Read method
        """
        if len(self.discord_audio):
            frame = self.discord_audio.popleft()
            return frame
        else:
            return None  # Do not emit an audio frame
