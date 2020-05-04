#!/usr/bin/env python3
# -*- coding: latin-1 -*-

# https://github.com/RobotCasserole1736/CasseroleDiscordBotPublic/blob/master/casseroleBot.py

import os
import sys
import discord
import asyncio
import ctypes
import ctypes.util
import configparser

from Softphone.Softphone import Softphone
from Audio import BufferIO, AudioCB # Must be below softphone import if not pjmedia max ports error????

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
        self.account.unregister()
        print("[DiscordPhone..]: Object destroyed.")


    async def on_ready(self):
        print("[DiscordPhone..]: Logged in as:", self.user.name, "-", self.user.id)
        print("[DiscordPhone..]: Running version:", discord.__version__)
        print("[DiscordPhone..]: Initializing softphone object.")
        self.softphone = Softphone()
        self.softphone.set_null_sound_device()

        print("[DiscordPhone..]: Attempting SIP registration...")
        #self.inbound=self.softphone.register(...)
        self.outbound=self.softphone.register(
            server  =self.config['server'],
            port    =self.config['port'],
            username=self.config['username'],
            password=self.config['secret']
        )
        print("[DiscordPhone..]: I am now ready.")


    # Handle commands
    async def on_message(self, command):

        # Do not listen to self (bot repeats commands)
        if command.author == self.user:
            return False


        # Quit / die
        if command.content.lower().startswith("!quit"):
            if self.voiceclient:
                await self.voiceclient.disconnect()
            await command.channel.send("Goodbye..!")
            await self.logout()


        # Leave voice channel
        if command.content.lower().startswith("!leave"):
            if self.voiceclient:
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
        if command.content.lower().startswith("!call"):# call, number, spoof
            cmd = command.content.lower().split(" ") # ["!call", "97526703", "13371337"]
            if len(cmd) != 3:
                await command.channel.send("Correct usage: !call <number to call (with 00 for country code)> <caller id>")
                print("[DiscordPhone..]: Parameter error!")
                return
            number = cmd[1]
            caller_id = cmd[2]
            sip_uri = 'sip:%s@%s:%s' % (number, self.config['server'], self.config['port'])

            try:
                self.softphone.create_audio_stream(self.audio_buffer) # Move this inside call maybe?
                self.voiceclient.listen(discord.UserFilter(self.audio_buffer, command.author))
                self.voiceclient.play(self.audio_buffer)
                self.softphone.call(self.outbound, sip_uri)
                await command.channel.send("Calling: " + number + " with caller ID: " + caller_id)
            except error as e:
                await command.channel.send("Could not perform call - error:" + str(e))


        # Hangup phone call
        if command.content.lower().startswith("!hangup"):
            try:
                self.softphone.end_call()
                self.softphone.destroy_audio_stream() # Move this inside end_call maybe?
                await command.channel.send("Call with " + number + " ended.")
            except error as e:
                await command.channel.send("Could not end call - error:" + str(e))
            # Stop audio transmission
            #self.softphone.stop_playing()
            #self.softphone.stop_listening()
            #self.voiceclient.stop_playing()
            #self.voiceclient.stop_listening()



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

