import discord
import threading
import asyncio
import time, math
import sounddevice as sd
import wave
import numpy as np


# Makes woooooOOOOOoooooOOOOOooooOOOOOoo sounds
class TestAudioSource(discord.PCMAudio):
    def __init__(self, freq=440, duration_ms=20):

        #PCM Audio encoding constants
        self.SAMP_PERIOD_SEC = 1.0/48000.0 #48 KHz
        self.NUM_SAMPLES = int((duration_ms/1000.0)/self.SAMP_PERIOD_SEC)
        self.BYTES_PER_SAMP = 4 #Stereo, 16-bit
        self.NUM_BYTES = self.NUM_SAMPLES * self.BYTES_PER_SAMP
        self.CENTER_DATA_VAL = int(32768) # 16 bit encoding

        #Test tone constants
        self.freq = freq #Audio frequency of the wooooo
        self.beatFreq = 0.25 #modulation frequency of the woooOOOOOoooOOOOooooOOOO
        self.volume = 0.50 #0 to 1 range for how loud wooooo should be
        self.time = 0.0 #This audio source's playback time, in seconds.
        

        #Audio data storage buffers
        self.data = [0]*self.NUM_SAMPLES
        self.audio_bytes = [0]*self.NUM_BYTES

    def populateTestTone(self):
        for n in range(0, self.NUM_SAMPLES):
            self.data[n] = self.volume*math.sin(2*math.pi*self.time*self.freq)*math.sin(2*math.pi*self.time*self.beatFreq)
            self.time += self.SAMP_PERIOD_SEC

    def encodeToPCM(self):
        for sample_idx in range(0, self.NUM_SAMPLES):
            #Calcualte byte indicies for this sample - 4 bytes/sample (2 bytes/channel, 2 channels - left & right)
            left_lower_byte_idx = sample_idx*self.BYTES_PER_SAMP
            left_upper_byte_idx = left_lower_byte_idx + 1
            right_lower_byte_idx = left_lower_byte_idx + 2
            right_upper_byte_idx = left_lower_byte_idx + 3

            #PCM is Expecting signed, 16-bit integers, centered at 0, two's compliment 
            # self.data array is floating point, in range -1 to 1
            val = self.data[sample_idx]
            sample_val_int = int(round(val*self.CENTER_DATA_VAL)) 

            #Pack samples
            self.audio_bytes[left_lower_byte_idx] = sample_val_int & 0xFF
            self.audio_bytes[left_upper_byte_idx] = sample_val_int >> 8 & 0xFF
            self.audio_bytes[right_lower_byte_idx] = sample_val_int & 0xFF
            self.audio_bytes[right_upper_byte_idx] = sample_val_int >> 8 & 0xFF

    def decodeFromPCM(self, audioBytes, data):
        for sample_idx in range(0, self.NUM_SAMPLES):
            #Calcualte byte indicies for this sample - 4 bytes/sample (2 bytes/channel, 2 channels - left & right)
            left_lower_byte_idx = sample_idx*self.BYTES_PER_SAMP
            left_upper_byte_idx = left_lower_byte_idx + 1
            right_lower_byte_idx = left_lower_byte_idx + 2
            right_upper_byte_idx = left_lower_byte_idx + 3

            valLeft  = float((audioBytes[left_lower_byte_idx]  + audioBytes[left_upper_byte_idx]  * 256) / self.CENTER_DATA_VAL)
            if(valLeft > 1.0):
                valLeft = valLeft - 2.0

            valRight = float((audioBytes[right_lower_byte_idx] + audioBytes[right_upper_byte_idx] * 256) / self.CENTER_DATA_VAL)
            if(valRight > 1.0):
                valRight = valRight - 2.0

            sampleValFloat = (0.5*valLeft + 0.5*valRight)

            data[sample_idx] = sampleValFloat

    # Required by discord.PCMAudio 
    # Calcualtes and returns 20ms of PCM-encoded byte audio data
    def read(self):
        self.populateTestTone()
        self.encodeToPCM()
        return bytes(self.audio_bytes)



# Gets audio from the microphone
class MicrophoneAudioSource(discord.PCMAudio):
    def __init__(self,  duration_ms=20):
        self.SAMP_RATE_HZ = 48000.0 #48 KHz
        self.SAMP_PERIOD_SEC = 1.0/self.SAMP_RATE_HZ
        self.NUM_SAMPLES = int((duration_ms/1000.0)/self.SAMP_PERIOD_SEC)
        self.audioStream = sd.RawInputStream(samplerate=self.SAMP_RATE_HZ, channels=2, dtype='int16', blocksize=self.NUM_SAMPLES)
        self.audioStream.start()


    def read(self):
        retVal = self.audioStream.read(self.NUM_SAMPLES)
        rawData = bytes(retVal[0])
        return rawData


# Gets audio from a local .wav file
# Assumes .wav file is 16-bit 48KHz stereo PCM
class WaveFileAudioSource(discord.PCMAudio):
    def __init__(self, file):
        self.READ_CHUNK_SIZE = 3840 #magic number of bytes that 20ms worth of 16-bit 48KHz stereo PCM should oc
        self.audioData = None
        self.byteIndex = 0
        with wave.open(file, mode='rb') as wavef:
            # Buffer the whole file into RAM. 
            # Hopefully the files aren't too big. Heh.
            self.numBytes = wavef.getnframes()*4
            print("Reading in {} bytes from {}".format(self.numBytes, file))
            self.audioData = bytearray(wavef.readframes(wavef.getnframes()))

    def read(self):
        if(self.audioData is not None):
            startIdx = self.byteIndex
            endIdx = (self.byteIndex + self.READ_CHUNK_SIZE - 1)
            outputData = self.audioData[startIdx:endIdx]

            self.byteIndex = self.byteIndex + self.READ_CHUNK_SIZE

            # Do Looping
            if(self.byteIndex >= self.numBytes):
                self.byteIndex = 0

            return bytes(outputData)
        else:
            return None

# Puts audio to the speakers
class SpeakerAudioSink(discord.AudioSink):
    def __init__(self,  duration_ms=20):
        self.SAMP_RATE_HZ = 48000.0 #48 KHz
        self.SAMP_PERIOD_SEC = 1.0/self.SAMP_RATE_HZ
        self.NUM_SAMPLES = int((duration_ms/1000.0)/self.SAMP_PERIOD_SEC)

        self.BYTES_PER_SAMP = 4 #Stereo, 16-bit
        self.NUM_BYTES = self.NUM_SAMPLES * self.BYTES_PER_SAMP
        self.CENTER_DATA_VAL = int(32768) # 16 bit encoding

        self.curSpeakerID = None

        self.speakerIDList = []

        self.audio_bytes = np.ndarray(shape=(self.NUM_SAMPLES,2), dtype='<i2')
        self.audio_bytes.fill(0)

        self.rx_count = 0
        self.mixedPacketCount = 0

        self.audioStream = sd.OutputStream(samplerate=self.SAMP_RATE_HZ, channels=2, dtype='int16', blocksize=self.NUM_SAMPLES)
        self.audioStream.start()

    def write(self, voiceData):
        start = time.time()
        self.rx_count += 1

        if(voiceData.user is not None):
            speakerID = voiceData.user.id
            self.curSpeakerID = speakerID

            voiceDataNp = np.ndarray(shape=(self.NUM_SAMPLES,2), dtype='<i2', buffer=voiceData.data)

            if(speakerID in self.speakerIDList):
                self.audioStream.write(self.audio_bytes)
                self.audio_bytes.fill(0)
                self.speakerIDList = []
                self.mixedPacketCount += 1
            
            self.audio_bytes += voiceDataNp
            self.speakerIDList.append(speakerID)

            elapsed = time.time() - start
            #if(self.rx_count % 10 == 0):
            #    print("{}s | {} packets from Discord | {} packets sent to speaker | {} Speaking. ".format(elapsed, self.rx_count, self.mixedPacketCount, voiceData.user.name))   


            return




# Does Nothing (for now)
class NullAudioSink(discord.AudioSink):
    def __init__(self,  duration_ms=20):
        self.curSpeakerID = None
        pass

    def write(self, voiceData):
        pass