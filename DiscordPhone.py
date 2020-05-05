#!/usr/bin/env python3
# -*- coding: latin-1 -*-
# Built with pjproject: https://github.com/nicolaipre/pjproject
# It is important to use this ^ fork! 


# https://github.com/RobotCasserole1736/CasseroleDiscordBotPublic/blob/master/casseroleBot.py

import os
import sys
import time
import discord
import asyncio
import ctypes
import socket
import ctypes.util
import configparser

from threading import Thread

from Softphone.Softphone import Softphone
from Audio import AudioCB # Must be below softphone import if not pjmedia max ports error????

# Fix Discord Opus error
discord.opus.load_opus(ctypes.util.find_library('opus'))
discord.opus.is_loaded()

class DiscordPhone(discord.Client):
    def __init__(self, sip_config):
        super().__init__()

        # SIP
        self.config = sip_config
        self.inbound = None
        self.outbound = None

        # Audio
        self.softphone = None
        self.voiceclient = None
        self.audio_buffer = AudioCB()


    def __del__(self):
        self.softphone.unregister(self.outbound)
        #self.outbound.delete()
        print("[DiscordPhone..]: Object destroyed.")


    async def on_ready(self):
        print("[DiscordPhone..]: Logged in as:", self.user.name, "-", self.user.id)
        print("[DiscordPhone..]: Running version:", discord.__version__)
        print("[DiscordPhone..]: Initializing softphone object.")
        self.softphone = Softphone()
        self.softphone.set_null_sound_device()

        print("[DiscordPhone..]: Attempting SIP registration...")
        #self.inbound=self.softphone.register(...) # TODO: Registration of account for incoming calls
        self.outbound=self.softphone.register(
            server  =self.config['server'],
            port    =self.config['port'],
            username=self.config['username'],
            password=self.config['secret']
        )
        print("[DiscordPhone..]: I am now ready.")



    async def set_caller_id(self, caller_id):
        pass
        # sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # conn = sock.connect(('127.0.0.1', '5038'))
        #        sock.send("""
        # action:updateconfig
        # 
        # """)
        #        sock.send("\r\n")
        # data = sock.recv()
        # sock.close()
        # netcat connection to 5038, username + password -> action:updateconfig
        # https://gist.github.com/jfinstrom/4227521
        # https://pypi.org/project/asterisk-ami/
        # https://www.voip-info.org/asterisk-manager-api-action-updateconfig/
        # https://stackoverflow.com/questions/32781655/asterisk-ami-deleting-of-certain-extension
        # https://stackoverflow.com/questions/47938769/updateconfig-asterisk-extensions-conf
        """
        Action: updateconfig
        Reload: yes
        Srcfilename: extensions.conf
        Dstfilename: extensions.conf
        Action-000000: delete
        Cat-000000: test
        Var-000000: exten
        Match-000000: Bob


        action:updateconfig
        srcfilename:extensions.conf
        dstfilename:extensions.conf
        Action-000000: update
        Cat-000000: stdexten
        Var-000000: exten
        Match-000000: _X.,50005,Dial(${dev},20)
        Value-000000:>_X.,50005,Dial(${dev},30)
        """



    async def motherfucker(self):
        print("Enter mf")
        #self.voiceclient.listen(discord.UserFilter(self.audio_buffer, command.author))
        self.voiceclient.play(self.audio_buffer)
        print("Leave mf")




    # Handle commands
    async def on_message(self, command):

        # Do not listen to self (bot repeats commands)
        if command.author == self.user:
            return False

        # List available commands
        if command.content.lower().startswith("!commands"):
            await command.channel.send("""```Available commands:
!join   -   join a voice channel
!leave  -   leave a voice channel
!quit   -   shut down bot
!hop    -   hop to voice channel
!call   -   call a phone number
!hangup -   end a call
```""")

        # Quit / die
        if command.content.lower().startswith("!quit"):
            if self.voiceclient:
                await self.voiceclient.disconnect()
            await command.channel.send("Goodbye..!")
            await self.logout()


        # Leave voice channel
        if command.content.lower().startswith("!leave"):
            if self.voiceclient:
                await command.channel.send("Leaving voice channel: " + command.author.voice.channel.name)
                await self.voiceclient.disconnect()
            else:
                await command.channel.send("Sorry, I am not in a voice channel...")


        # Hop voice channel
        if command.content.lower().startswith("!hop"):
            if self.voiceclient:
                await self.voiceclient.move_to(command.author.voice.channel)
            else:
                await command.channel.send("Sorry, I am not in a voice channel. You will have to summon me first.")


        # Join voice channel
        if command.content.lower().startswith("!join"):
            if command.author.voice is None:
                await command.channel.send("Sorry, you are not in a voice channel.")
            else:
                await command.channel.send("Joining voice channel: " + command.author.voice.channel.name)
                self.voiceclient = await command.author.voice.channel.connect()
                #self.voiceclient.play("elevator-waiting-music.wav")


        # Call phone
        if command.content.lower().startswith("!call"): # call, number, spoof
            cmd = command.content.lower().split(" ") # ["!call", "97526703", "13371337"] # replace number in /etc/asterisk/extensions.conf, ssh?
            # https://community.asterisk.org/t/persuade-asterisk-to-reload-config-files-from-python/20056

            # 1. sed replace /etc/asterisk/extensions.conf
            # service asterisk reload

            if len(cmd) != 3:
                await command.channel.send("Correct usage: !call <number to call (with 00 for country code)> <caller id>")
                return

            number = cmd[1]
            caller_id = cmd[2]
            sip_uri = 'sip:%s@%s:%s' % (number, self.config['server'], self.config['port'])


            try:
                self.softphone.create_audio_stream(self.audio_buffer) # Move this inside call maybe?
                self.softphone.call(self.outbound, sip_uri)
                
                
                import pjsua as pj
                while self.softphone.current_call.info().media_state != pj.MediaState.ACTIVE: # Move to softphone or call handler 
                    time.sleep(0.1)
                


                self.voiceclient.listen(discord.UserFilter(self.audio_buffer, command.author))
                #self.voiceclient.play(self.audio_buffer) # wait with this since listen and play cant be in same block here IIRC...?


                # TODO: Why does this have to be in its own loop? 
                # This does not need them in own loop - https://github.com/RobotCasserole1736/CasseroleDiscordBotPublic/blob/master/casseroleBot.py#L141
                #loop = asyncio.get_event_loop()
                #loop.create_task(self.motherfucker())
                self.loop.create_task(self.motherfucker())  # einar aka PythonGawd NeverForGet # <-- neger 

                await command.channel.send("Calling: " + number + " with Caller-ID: " + caller_id)

            except Error as e:
                await command.channel.send(f"Could not perform call - Error: {e}")


        # TODO: Add multiple mics:
        # https://github.com/RobotCasserole1736/CasseroleDiscordBotPublic/blob/master/audioHandling.py#L159
        



        # Hangup phone call
        if command.content.lower().startswith("!hangup"):
            try:
                self.softphone.end_call()
                self.voiceclient.stop_playing()
                self.voiceclient.stop_listening()
                self.softphone.destroy_audio_stream() # Move this inside end_call maybe?
                await command.channel.send("Call ended.")

            except Error as e:
                await command.channel.send("Could not end call - Error:" + str(e))




# TODO: Replace with proper parser
def read_config(file_name):
    #if os.path != file_name: sys.exit("No config file found!")
    cfg = configparser.RawConfigParser()
    cfg.read(file_name)
    return dict(cfg)


config = read_config('dp.conf')
token  = config['DISCORD']['token']
client = DiscordPhone(config['SIP'])
client.run(token)

