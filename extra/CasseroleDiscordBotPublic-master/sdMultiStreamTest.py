import time, math
import sounddevice as sd


# Makes woooooOOOOOoooooOOOOOooooOOOOOoo sounds
class TestAudioSource():
    def __init__(self, freq=440, duration_ms=20):

        #PCM Audio encoding constants
        self.SAMP_RATE_HZ = 48000.0 #48 KHz
        self.SAMP_PERIOD_SEC = 1.0/self.SAMP_RATE_HZ
        self.NUM_SAMPLES = int((duration_ms/1000.0)/self.SAMP_PERIOD_SEC)
        self.BYTES_PER_SAMP = 4 #Stereo, 16-bit
        self.NUM_BYTES = self.NUM_SAMPLES * self.BYTES_PER_SAMP
        self.CENTER_DATA_VAL = int(32768) # 16 bit encoding

        #Test tone constants
        self.freq = freq #Audio frequency of the wooooo
        self.beatFreq = 0.25 #modulation frequency of the woooOOOOOoooOOOOooooOOOO
        self.volume = 1.0 #0 to 1 range for how loud wooooo should be
        self.time = 0.0 #This audio source's playback time, in seconds.
        

        #Audio data storage buffers
        self.data1 = [0]*self.NUM_SAMPLES
        self.data2 = [0]*self.NUM_SAMPLES
        self.audio_bytes1 = [0]*self.NUM_BYTES
        self.audio_bytes2 = [0]*self.NUM_BYTES

        self.stream = sd.RawOutputStream(samplerate=self.SAMP_RATE_HZ, channels=2, dtype='int16', blocksize=self.NUM_SAMPLES)
        self.stream.start()

    def populateTestTone(self):
        for n in range(0, self.NUM_SAMPLES):
            self.data1[n] = self.volume*math.sin(2*math.pi*self.time*self.freq)*math.sin(2*math.pi*self.time*self.beatFreq)
            self.data2[n] = self.volume*math.sin(2*math.pi*self.time*self.freq*2)
            self.time += self.SAMP_PERIOD_SEC

    def encodeToPCM(self, data, audioBytes):
        for sample_idx in range(0, self.NUM_SAMPLES):
            #Calcualte byte indicies for this sample - 4 bytes/sample (2 bytes/channel, 2 channels - left & right)
            left_lower_byte_idx = sample_idx*self.BYTES_PER_SAMP
            left_upper_byte_idx = left_lower_byte_idx + 1
            right_lower_byte_idx = left_lower_byte_idx + 2
            right_upper_byte_idx = left_lower_byte_idx + 3

            #PCM is Expecting signed, 16-bit integers, centered at 0, two's compliment 
            # self.data array is floating point, in range -1 to 1
            val = data[sample_idx]
            sample_val_int = int(round(val*self.CENTER_DATA_VAL)) 

            #Pack samples
            audioBytes[left_lower_byte_idx] = sample_val_int & 0xFF
            audioBytes[left_upper_byte_idx] = sample_val_int >> 8 & 0xFF
            audioBytes[right_lower_byte_idx] = sample_val_int & 0xFF
            audioBytes[right_upper_byte_idx] = sample_val_int >> 8 & 0xFF

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

    def mixAudioStreams(self, stream1, stream2):
        returnArray = [0]*self.NUM_SAMPLES
        for sample_idx in range(0, self.NUM_SAMPLES):
            val = stream1[sample_idx] + stream2[sample_idx]
            if(val > 1.0):
                val = 1.0
            elif(val < -1.0):
                val = -1.0
            returnArray[sample_idx] = val
        return returnArray
            

    # Required by discord.PCMAudio 
    # Calcualtes and returns 20ms of PCM-encoded byte audio data
    def update(self):
        self.populateTestTone()

        self.encodeToPCM(self.data1, self.audio_bytes1)
        self.encodeToPCM(self.data2, self.audio_bytes2)

        #Try to add the two streams
        #summedAudio = [0]*self.NUM_SAMPLES
        #writeBytes  = [0]*self.NUM_BYTES

        #streamData = [0]*self.NUM_SAMPLES
        #self.decodeFromPCM(self.audio_bytes1, streamData)
        #summedAudio = self.mixAudioStreams(summedAudio, streamData)

        #self.decodeFromPCM(self.audio_bytes2, streamData)
        #summedAudio = self.mixAudioStreams(summedAudio, streamData)

        #self.encodeToPCM(summedAudio, writeBytes)

        self.stream.write(bytes(self.audio_bytes2))


### Main code exection
src = TestAudioSource()

for i in range(0,1000):
    src.update()
    time.sleep(0.02)

