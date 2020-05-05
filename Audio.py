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
        
        # Multi user mic hack:
        self.audio_bytes = bytearray()

        self.curSpeakerID = None
        self.speakerIDList = []



    
    ### phone -> discord ###

    def cb_put_frame(self, frame): # Denne er good! Testet med loopback i telefon
        """Listen to the audio coming from phone, and write to phone_audio buffer.
            
           Phone: Write method
        """
        # An audio frame arrived, it is a string (i.e. ByteArray)
        self.phone_audio.append(frame)
        #print(len(frame))
        # Return an integer; 0 means success, but this does not matter now
        return 0



    # Denne er fucka...
    def read(self):
        """Read from discord_audio buffer, and send audio to phone.
        
        - Get an audio frame to be played into phone speaker.

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
        """Listen to the audio coming from Discord, and write to discord_audio buffer.
        """
        self.discord_audio.append(voiceData.data) # raw bytes from VoiceData object.
        #print("WRITE bytes from discord:", len(data.data), "| Buffer size:", len(self.discord_audio))


        # TODO: Add multiple mics:
        # https://github.com/RobotCasserole1736/CasseroleDiscordBotPublic/blob/master/audioHandling.py#L159

        """
        # Attempt to let everyone speak:
        if (voiceData.user is not None):
            speakerID = voiceData.user.id
            self.curSpeakerID = speakerID # used to update bot text
         
            if (speakerID in self.speakerIDList):
                frame            = self.audio_bytes[:self.samples_per_frame] # Get enough samples to fill a frame
                self.audio_bytes = self.audio_bytes[self.samples_per_frame:] # Pop
                self.discord_audio.append(frame)
                self.speakerIDList = []
            
            self.audio_bytes += voiceData.data
            self.speakerIDList.append(speakerID)
        """

        



    def cb_get_frame(self, size): # Denne er good! Testet med loopback i telefon
        """Read from discord_audio buffer, and send audio to phone.
        
        - Get an audio frame to be played into phone speaker.

        1 frame = 640 bytes of audio
        """
        if len(self.discord_audio):
            frame = self.discord_audio.popleft()
            return frame
        else:
            return None  # Do not emit an audio frame
