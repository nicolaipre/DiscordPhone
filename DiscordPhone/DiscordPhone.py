#!/usr/bin/env python3
# -*- coding: latin-1 -*-
# Built with pjproject: https://github.com/nicolaipre/pjproject
# It is important to use this ^ fork!

import os
import sys
import time
import discord
import asyncio
import ctypes
import socket
import ctypes.util

from .Softphone.Softphone import Softphone
from .Audio import AudioCB # Must be below softphone import if not pjmedia max ports error????
from .Asterisk import Asterisk


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

        # Run subroutines
        #self.speakingUserString = "..."
        #self.loop.create_task(self.subroutines())


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


    async def subroutines(self):
        if self.voiceclient:
            member = self.voiceclient.get_member(self.audioSink.curSpeakerID)
            if (member is not None):
                if member.nick is not None:
                    self.speakingUserString = str(member.nick)
                else:
                    self.speakingUserString = str(member)

            self.bot.change_presence(discord.Game(name=f"Talking: {self.speakingUserString}"))


    async def play_thread(self):
        #print("Enter mf")
        self.voiceclient.play(self.audio_buffer)
        #print("Leave mf")



    # Handle commands TODO: replace with decorator command handling..?
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
                await command.channel.send(f"Leaving voice channel: {command.author.voice.channel.name}")
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
                await command.channel.send(f"Joining voice channel: {command.author.voice.channel.name}")
                self.voiceclient = await command.author.voice.channel.connect()
                #self.voiceclient.play("elevator-waiting-music.wav")


        # Call phone
        if command.content.lower().startswith("!call"): # call, number, spoof
            cmd = command.content.lower().split(" ") # ["!call", "97526703", "13371337"] # replace number in /etc/asterisk/extensions.conf, ssh?

            if len(cmd) != 3:
                await command.channel.send("Correct usage: `!call <number to call (with country code)> <Caller ID>`")
                await command.channel.send("Example usage: `!call +4712345678 +4713371337`")
                return

            number = cmd[1]
            caller_id = cmd[2]

            # TODO: Fix this ghetto approach of replacing and stripping
            number_new    = number.replace("+", "00")
            caller_id_new = caller_id[1:] # Strip starting +
            print(caller_id_new)

            #sip_uri = 'sip:%s@%s:%s' % (number, self.config['server'], self.config['port'])
            sip_uri = f"sip:{number_new}@{self.config['server']}:{self.config['port']}"

            try:
                a = Asterisk(host='127.0.0.1', port=5038, username='admin', password='admin')
                a.set_caller_id(caller_id_new)

            except Exception as e:
                await command.channel.send(f"Could not set caller ID - Error: {e}")



            try:
                self.softphone.create_audio_stream(self.audio_buffer) # Move this inside call maybe?
                self.softphone.call(self.outbound, sip_uri)
                self.softphone.wait_for_active_audio() # Wait for active audio before we listen...
                #self.voiceclient.listen(discord.UserFilter(self.audio_buffer, command.author)) # Single speaker
                self.voiceclient.listen(self.audio_buffer) # Multiple speakers


                # TODO: Why does play() have to be in its own loop? Is it not threaded??? It is blocking???
                # This does not need them in own loop - https://github.com/RobotCasserole1736/CasseroleDiscordBotPublic/blob/master/casseroleBot.py#L141
                loop = asyncio.get_event_loop()
                loop.create_task(self.play_thread())# einar aka PythonGawd NeverForGet (hack the loop)

                await command.channel.send(f"Calling: `{number}` with Caller-ID: `{caller_id}`")

            except Exception as e:
                await command.channel.send(f"Could not perform call - Error: {e}")



        # Hangup phone call
        if command.content.lower().startswith("!hangup"):
            try:
                self.softphone.end_call()
                self.voiceclient.stop_playing()
                self.voiceclient.stop_listening()
                self.softphone.destroy_audio_stream() # Move this inside end_call maybe?
                await command.channel.send("Call ended.")

            except Exception as e:
                await command.channel.send(f"Could not end call - Error: {e}")

        """
        # Unmute mic
        if command.content.lower().startswith("!unmute"):
            self.AudioCB.speakerIDList.append(command.message.author.id)
            await command.channel.send(f"Adding user {command.message.author.name} to call.")


        # Mute mic
        if command.content.lower().startswith("!mute"):
            self.AudioCB.speakerIDList.remove(command.message.author.id)
            await command.channel.send(f"Removing user {command.message.author.name} from call.")
        """

        if command.content.lower().startswith("!a"):
            #await self.change_presence(
            #    status   = discord.Status.idle,
            #    activity = discord.Game(name="Test...")
            #)
            await self.change_presence(
                status   = discord.Status.online,
                activity = discord.Activity(
                    type = discord.ActivityType.listening,
                    name = "Call: x"
                )
            )

