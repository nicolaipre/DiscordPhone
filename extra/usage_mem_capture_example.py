#!/usr/bin/env python3

import pjsuaxt
import multiprocessing



# GET CALL-AUDIO from memory, and send to DISCORD:
while(isRecording and isPlaying):

    # Get discord audio, put onto memory (send to call)
    if (mem_player.get_write_available() > SAMPLES_PER_FRAME*2): # why *2?
        discord_audio = discordBufferSink.read(num_samples) # discord_audio = vc.listen()
        mem_player.put_frame(discord_audio) # frame = raw pcm sample data ( Frame.payload ), returns last frame id

    # Get call audio from memory, send it to discord
    if (mem_capture.get_read_available() > SAMPLES_PER_FRAME*2):
        call_audio = mem_capture.get_frame() # get audio from pjsip memory
        callBufferSink.write(call_audio)
        # vc.play(call_audio) ?

