#!/usr/bin/env python3
# -*- coding: latin-1 -*-
# coding=utf-8

import discord
import asyncio
import ctypes
import ctypes.util
import configparser
import multiprocessing
from Softphone.Softphone import Softphone
from Audio import DiscordBuffer, SoftphoneBuffer
from Casserole import TestAudioSource

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
        self.softphone = None
        self.call_audio = SoftphoneBuffer()

        # Discord
        self.voiceclient   = None
        self.test_audio    = TestAudioSource()
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
            server  =self.config['server'],
            port    =self.config['port'],
            username=self.config['username'],
            password=self.config['secret']
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
                await command.channel.send("Joining voice channel: " + command.author.voice.channel.name)
                self.voiceclient = await command.author.voice.channel.connect()

                #self.voiceclient.play("elevator-waiting-music.wav")
                # TODO: Implement listen() and play() using MultiProcessing.Pipe() with SIP.py
                #self.voiceclient.listen(discord.UserFilter(...))


        # Call a phone
        if command.content.lower().startswith("!call"):# call, number, spoof
            cmd = command.content.lower().split(" ") # ["!call", "97526703", "13371337"]
            if len(cmd) != 3:
                print("param error")
                return
            number = cmd[1]
            sip_uri = 'sip:%s@%s:%s' % (number, self.config['server'], self.config['port'])

            self.softphone.call(self.outbound, sip_uri)

            #self.voiceclient.listen(discord.UserFilter(self.discord_audio, command.author))
            #self.softphone.listen(self.call_audio)
            #self.softphone.play(self.discord_audio) # Transmit discord audio to call
            #self.voiceclient.play(self.call_audio)  # Transmit call audio to discord



        # Transmit phone audio to discord
        if command.content.lower().startswith("!phone2discord"):
            self.softphone.listen(self.call_audio) # listen to call, write to buffer call_audio
            self.voiceclient.play(self.call_audio)


        # Transmit discord audio to phone
        if command.content.lower().startswith("!discord2phone"):
            self.voiceclient.listen(discord.UserFilter(self.discord_audio, command.author))
            self.softphone.play(self.discord_audio)


        # Test audio source
        if command.content.lower().startswith("!testaudio"):
            self.softphone.play(self.test_audio)


        # Record phone to file
        if command.content.lower().startswith("!recphone"):
            self.softphone.capture("call-audio.wav")
            #self.softphone.playback("oleivars-fix.wav")


        # Record discord to file
        if command.content.lower().startswith("!recdiscord"):
            self.voiceclient.listen(discord.UserFilter(discord.WaveSink('discord-audio.wav'), command.author))


        # Stop capturing/recording
        if command.content.lower().startswith("!stoprec"):
            self.softphone.stop_capturing()


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


def read_config(file_name):
    # if os.path!== file_name: sys.exit(no config file gfound!)
    cfg = configparser.RawConfigParser()
    cfg.read(file_name)
    return dict(cfg)


config = read_config('dp.conf')

token = config['DISCORD']['token']

client = DiscordPhone(config['SIP'])
client.run(token)

