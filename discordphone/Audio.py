#!/usr/bin/env python3
# -*- coding: latin-1 -*-

import discord
import logging
import sounddevice as sd
from collections import deque

# NOTE: Remember to set sample_rate to be same as system audio. But does it even help..?
# Can be checked with command "$ pacmd list-sinks | grep 'sample spec'"

logger = logging.getLogger(__name__)

class AudioCB(discord.PCMAudio, discord.reader.AudioSink): # DO NOT DELETE. MIXING IS IN THIS ONE!!!

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


    # Phone --> Discord

    def cb_put_frame(self, frame): # Tested and works
        """ Listen to the audio coming from phone, and write to phone_audio buffer.

            Phone: Write method
        """
        # An audio frame arrived, it is a string (i.e. ByteArray)
        self.phone_audio.append(frame)
        #print(len(frame))
        # Return an integer; 0 means success, but this does not matter now
        return 0

    def read(self):
        """ Read from discord_audio buffer, and send audio to phone.

            Get an audio frame to be played into phone speaker.

            Discord: Read method
        """
        if len(self.phone_audio):
            frame = self.phone_audio.popleft()
            return bytes(frame)
        else:
            print("empty frame of null bytes RETURNED") # play stops when we run out of frames. hmm.
            return b'\x00' * self.samples_per_frame  # Return an empty frame of null bytes


    # Discord --> Phone

    def write(self, voiceData):
        """ Listen to the audio coming from Discord, and write to discord_audio buffer.

            Discord: Write method
        """

        #print(f"{voiceData.user}\t- FrameBytes: {[n for n in voiceData.data[:30]]}")
        #self.discord_audio.append(voiceData.data) # appends a frame of voice data

        speaker_id = voiceData.user.id

        if speaker_id in self.speakers:
            # amount of speakers is len(self.speakers)
            speakerAmount = len(self.tmp_audio_bytes)
            frame = [0] * 3840 # TODO: Replace 3840 with frame_size, calculated based on sample rate! Only works with 48000 at the moment.

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


    def cb_get_frame(self, size):
        """ Read from discord_audio buffer, and send audio to phone.

            Get an audio frame to be played into phone speaker.

            Phone: Read method
        """
        if len(self.discord_audio):
            frame = self.discord_audio.popleft()
            return frame
        else:
            return None


class MicrophoneAudioSource(discord.PCMAudio):
    """ Receive audio from system microphone (source).
    """
    def __init__(self, duration_ms=20, sample_rate=48000.0, channel_count=2):
        self.duration_ms = duration_ms
        self.sample_rate = sample_rate
        self.sample_period_sec = 1.0/self.sample_rate
        self.samples_per_frame = int((duration_ms/1000.0) / self.sample_period_sec)
        self.audio_stream = sd.RawInputStream(samplerate=self.sample_rate, channels=channel_count, dtype='int16', blocksize=self.samples_per_frame)
        self.audio_stream.start()


    def read(self):
        ret = self.audio_stream.read(self.samples_per_frame)
        raw_samples = bytes(ret[0])
        return raw_samples


class SpeakerAudioSink(discord.reader.AudioSink):
    """ Send audio to system speaker (sink).
    """
    def __init__(self, duration_ms=20, sample_rate=48000.0, channel_count=2):
        self.duration_ms = duration_ms
        self.sample_rate = sample_rate
        self.sample_period_sec = 1.0/self.sample_rate
        self.samples_per_frame = int((duration_ms/1000.0) / self.sample_period_sec)
        self.audio_stream = sd.RawOutputStream(samplerate=self.sample_rate, channels=channel_count, dtype='int16', blocksize=self.samples_per_frame)
        self.audio_stream.start()


    def write(self, data):
        self.audio_stream.write(data.data)
