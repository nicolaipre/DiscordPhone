import soundfile as sf

myfile = sf.SoundFile('input.wav',mode='r',format='RAW',samplerate=16000,channels=1,subtype='PCM_16')

# Reconstruct wav file
sf.write('output.wav',myfile.read(),16000,subtype='PCM_16',format='WAV')



use import wave instead to write pcm samples to file...
