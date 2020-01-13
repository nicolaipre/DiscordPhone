#!/usr/bin/env python3

import discord
import asyncio
import ctypes
import ctypes.util
import configparser
import multiprocessing
from .Softphone.Softphone import Softphone
from Audio import DiscordBuffer, SoftphoneBuffer

# Fix Discord Opus error
discord.opus.load_opus(ctypes.util.find_library('opus'))
discord.opus.is_loaded()

class DiscordPhone(discord.Client, sip_config):
    def __init__(self):
        super().__init__()

        # SIP
        self.inbound = None
        self.outbound = None
        self.softphone = None
        self.call_audio = SoftphoneBuffer()

        # Discord
        self.voiceclient = None
        self.discord_audio = DiscordBuffer()


    def __del__(self):
        #self.account.unregister()
        print("[DiscordPhone]: Object destroyed.")


    async def on_ready(self):
        print("[DiscordPhone]: Logged in as:", self.user.name, ":", self.user.id)
        print("[DiscordPhone]: Running version:", discord.__version__)
        print("[DiscordPhone]: Initializing softphone object.")
        self.softphone = Softphone()
        self.softphone.set_null_sound_device()
        #self.inbound=self.softphone.register(...)
        self.outbound=self.softphone.register(
            server  =sip_config['server'],
            port    =sip_config['port'],
            username=sip_config['username'],
            password=sip_config['password']
        )
        print("[DiscordPhone]: Attempted SIP registration.")


    # Handle commands
    async def on_message(self, command):

        # Do not listen to self (when bot repeats commands)
        if command.author == self.user:
            return False


        # Quit
        if command.content.lower().startswith("!quit"):
            if self.voiceclient:
                await self.voiceclient.disconnect()

            await self.logout()


        # Leave
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
                await command.channel.send("Sorry, I am not in a voice channel, so you will have to summon me first.")


        # Join voice channel
        if command.content.lower().startswith("!join"):
            if command.author.voice is None:
                await command.channel.send("Sorry, you are not in a voice channel.")
            else:
                await command.channel.send("Joining voice channel", command.author.voice.channel.name)
                self.voiceclient = await command.author.voice.channel.connect()

                self.voiceclient.play("elevator-waiting-music.wav")
                # TODO: Implement listen() and play() using MultiProcessing.Pipe() with SIP.py
                #self.voiceclient.listen(discord.UserFilter(...))


        # Call a phone
        if command.content.lower().startswith("!call"):# call, number, spoof
            cmd = command.content.lower().split(" ") # ["!call", "97526703", "13371337"]
            number = cmd[1]
            sip_uri = 'sip:%s@%s:%s' % (number, sip_config['server'], sip_config['port'])

            self.softphone.call(outbound, sip_uri)
            self.softphone.play(self.discord_audio) # Transmit discord audio to call
            self.voiceclient.play(self.call_audio)  # Transmit call audio to discord


        # Answer incoming call
        if command.content.lower().startswith("!answer"):
            #self.softphone.answer(inbound)
            #self.softphone.play(self.discord_audio)
            #self.voiceclient.play(self.call_audio)
            raise NotImplementedError


        # Hangup phone call
        if command.content.lower().startswith("!hangup"):
            self.softphone.end_call()

            # Stop audio transmission
            #self.softphone.stop_playing()
            #self.softphone.stop_listening()
            #self.voiceclient.stop_playing()
            #self.voiceclient.stop_listening()

    #endDef
#endClass



# Main (make a bot.py out of this)
config = configparser.RawConfigParser()
config.read("DiscordPhone.conf")
config = dict(config.items())

client = DiscordPhone(config['SIP'])
client.run(config(['Discord']['token']))

