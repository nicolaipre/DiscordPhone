#!/usr/bin/env python3
# -*- coding: latin-1 -*-

import os
import sys
import time
import discord
import asyncio
import logging
import ctypes
import socket
import ctypes.util

from os import environ as env
from dotenv import load_dotenv

from softphone.Softphone import Softphone

from .Audio import AudioCB
from .Asterisk import Asterisk

# Fix Discord Opus error
discord.opus.load_opus(ctypes.util.find_library('opus'))
discord.opus.is_loaded()

logger = logging.getLogger(__name__)


class DiscordPhone(discord.Client):
    def __init__(self):
        super().__init__()

        self.pid = os.getpid() # TODO: Prevent multiple bots running.

        # SIP Accounts
        self.inbound = None
        self.outbound = None

        # Audio
        self.softphone = None
        self.voiceclient = None
        self.audio_buffer = AudioCB()

        # Blacklisted spoofs # TODO: Make blacklist.json
        self.blacklist = [
            '911', # Do not spoof this.
            # TODO: Add more...
        ]

        self.x = None


    def __del__(self):
        try:
            #self.softphone.unregister(self.inbound)
            self.softphone.unregister(self.outbound)
        except Exception as e:
            logger.info("Attempted unregistration, but account was never registered.")
        finally:
            logger.info("Object destroyed.")


    async def on_ready(self):
        logger.info(f"Logged in as: {self.user.name} - {self.user.id}")
        logger.info(f"Running version: {discord.__version__}")
        logger.info("Initializing softphone object.")
        self.softphone = Softphone()
        self.softphone.set_null_sound_device()

        logger.info("Attempting SIP registration...")
        #self.inbound=self.softphone.register(...) # TODO: Registration of account for incoming calls
        self.outbound = self.softphone.register(
            server    = env.get('SIP_OUTBOUND_HOST'),
            port      = env.get('SIP_OUTBOUND_PORT'),
            username  = env.get('SIP_OUTBOUND_USER'),
            password  = env.get('SIP_OUTBOUND_PASS')
        )
        logger.info("DiscordPhone is now ready.")


    # TODO: Make matching better, and store all numbers in blacklist.json
    def blacklist_check(self, number):
        if number in self.blacklist:
            return True
        return False


    # FIXME: Required to detect when a call ends, so we stop audio transmission...
    """
    def detect_ended_call(self): # https://github.com/g-farrow/soft_phone/blob/808131342d19fb5fd8c95fcc01f8a57c699af993/soft_phone/soft_phone.py#L228
        while self.softphone.current_call.is_valid():
            logger.info(f"{self.softphone.current_call}, {self.softphone.call_handler.call}")
            time.sleep(0.5)

        logger.info("Call has ended. Stopping audio transmission")
        self.voiceclient.stop_playing()
        self.voiceclient.stop_listening()
        self.softphone.destroy_audio_stream()
        logger.info("Stopped audio!")
        # self.x.join() # got 2 love race conditions!
    """

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
!mic    -   take ownership of mic.
!all    -   listen to everyone!
!hop    -   hop to voice channel
!call   -   call a phone number
!hangup -   end a call
```""")

        # Quit / die
        elif command.content.lower().startswith("!quit"):
            if self.voiceclient:
                await self.voiceclient.disconnect()
            
            self.softphone = None # To trigger __del__ softphone for graceful exit
            await command.channel.send("Goodbye..!")
            await self.logout()
            logger.info("Logging out")


        # Leave voice channel
        elif command.content.lower().startswith("!leave"):
            if self.voiceclient:
                await command.channel.send(f"Leaving voice channel: {command.author.voice.channel.name}")
                await self.voiceclient.disconnect()
                logger.info(f"Left voice channel")
            else:
                await command.channel.send("Sorry, I am not in a voice channel...")


        # Hop voice channel
        elif command.content.lower().startswith("!hop"):
            if self.voiceclient:
                await self.voiceclient.move_to(command.author.voice.channel)
                logger.info("Hopped to new voice channel")

            elif command.author.voice is None:
                await command.channel.send("Sorry, you are not in a voice channel.")

            else:
                await command.channel.send("Sorry, I am not in a voice channel. You will have to summon me first.")


        # Join voice channel
        elif command.content.lower().startswith("!join"):
            if command.author.voice is None:
                await command.channel.send("Sorry, you are not in a voice channel.")
            else:
                logger.info("Joining voice channel and connecting to gateway")
                await command.channel.send(f"Joining voice channel and attempting to connect to gateway.")
                self.voiceclient = await command.author.voice.channel.connect()
                await command.channel.send(f"Successfully connected to `{command.author.voice.channel.name}`.")
                logger.info("Successfully connected to voice gateway")


        # Call phone
        elif command.content.lower().startswith("!call"): # !call <number> <spoofs>
            if command.author.voice is None:
                await command.channel.send("Sorry, you are not in a voice channel.")
                return

            if not self.voiceclient:
                await command.channel.send("Sorry, I am not in a voice channel...")
                return

            # Ok in voice channel. Nice.
            cmd = command.content.lower().split(" ")

            if len(cmd) != 3:
                await command.channel.send("Correct usage:  `!call <number to call (with country code)> <caller-ID>`.")
                await command.channel.send("Example usage: `!call +4512345678 +4513371337`.")
                return

            # TODO: Fix this ghetto shit below
            number = cmd[1]
            caller_id = cmd[2]
            number_new = number.replace("+", "00")
            caller_id_new = caller_id[1:] # Strip starting +

            if self.blacklist_check(number):
                await command.channel.send("This caller ID is blacklisted..!")
                logger.info(f"Attempt to spoof blacklisted number {number}")
                return

            # Format SIP URI
            host = env.get('SIP_OUTBOUND_HOST')
            port = env.get('SIP_OUTBOUND_PORT')
            sip_uri = f"sip:{number_new}@{host}:{port}"
            logger.info(f"Generated destination SIP URI: {sip_uri}")

            try:
                a = Asterisk(
                    host     = env.get('ASTERISK_HOST'),
                    port     = env.get('ASTERISK_PORT'),
                    username = env.get('ASTERISK_USER'),
                    password = env.get('ASTERISK_PASS')
                )

                logger.info(f"Updating caller ID to: {caller_id_new}")
                a.set_caller_id(caller_id_new)

            except Exception as e:
                await command.channel.send(f"Could not set caller ID. Error: {e}")
                return

            try:
                logger.info("Registering thread")
                self.softphone.lib.thread_register("python call worker") # Correct usage? Read documentation.
                
                logger.info("Creating audio streams")
                self.softphone.create_audio_stream(self.audio_buffer) # Move this inside call maybe?
                
                logger.info(f"Performing outbound call to SIP URI: {sip_uri}")
                self.softphone.call(self.outbound, sip_uri)

                logger.info("Waiting for active audio before listening")
                self.softphone.wait_for_active_audio() # Wait for active audio before we listen...

                logger.info("Attempting to listen to audio")
                self.voiceclient.listen(discord.UserFilter(self.audio_buffer, command.author)) # Single speaker
                #self.voiceclient.listen(self.audio_buffer) # Multiple speakers, lol works.

                logger.info("Attempting to play audio")
                self.voiceclient.play(self.audio_buffer) # does it work here afterall?

                await command.channel.send(f"Calling: `{number}` with Caller-ID: `{caller_id}`.")
                await self.change_presence(
                    status   = discord.Status.online,
                    activity = discord.Activity(
                        type = discord.ActivityType.listening,
                        name = f"call: {number}"
                    )
                ) #

                #import threading
                #self.x = threading.Thread(target=self.detect_ended_call)
                #self.x.start()
                # Wait for / Detect end of call
                #await self.detect_ended_call()
                #print(self.softphone.current_call)


            except Exception as e:
                await command.channel.send(f"Could not perform call. Error: {e}")
                return


        # Take ownership of voice
        elif command.content.lower().startswith("!mic"):
            if command.author.voice is None:
                await command.channel.send("Sorry, you are not in a voice channel.")
                return

            if not self.voiceclient:
                await command.channel.send("Sorry, I am not in a voice channel...")
                return

            if self.softphone.current_call == None:
                await command.channel.send(f"Error: A call must have been started by someone else before you try taking the mic.")
                return

            await command.channel.send(f"`{command.author}` has taken the mic!`")
            self.voiceclient.stop_listening()
            self.voiceclient.listen(discord.UserFilter(self.audio_buffer, command.author)) # Single speaker


        # Listen to everyone!
        elif command.content.lower().startswith("!all"):
            if command.author.voice is None:
                await command.channel.send("Sorry, you are not in a voice channel.")
                return

            if not self.voiceclient:
                await command.channel.send("Sorry, I am not in a voice channel...")
                return

            if self.softphone.current_call == None:
                await command.channel.send(f"Error: A call must have been started by someone else before you try taking the mic.")
                return
            
            await command.channel.send(f"`Mic is open to everyone!`")
            self.voiceclient.stop_listening()
            self.voiceclient.listen(self.audio_buffer) # Multiple speakers


        # Listen to DiscordPhone
        elif command.content.lower().startswith("!self"):
            await command.channel.send(f"@mic")

        # Hangup phone call
        elif command.content.lower().startswith("!hangup"):
            try:
                logger.info("Attempting to end call")
                self.softphone.end_call()

                logger.info("Attempting to stop playing audio")
                self.voiceclient.stop_playing()

                logger.info("Attempting to stop listening for audio")
                self.voiceclient.stop_listening()

                logger.info("Attempting to destroy audio streams")
                self.softphone.destroy_audio_stream() # Move this inside end_call maybe?

                await command.channel.send("Call ended.")
                await self.change_presence(status=discord.Status.idle, activity=discord.Game(name="Idle..."))

            except Exception as e:
                await command.channel.send(f"Could not end call. Error: {e}")


        elif command.content.lower().startswith("!a"):
            #print(self.softphone.current_call)
            await command.channel.send(f"Call duration: `{self.softphone.get_call_length()} sec.`")
            pass

        
        # Trigger a 'wut-da-hell' on unknown command
        elif command.content.lower().startswith("!"):
            if self.voiceclient:
                if not self.voiceclient.is_playing():
                    self.voiceclient.play(discord.FFmpegPCMAudio('audio/wut-da-hell-sample.mp3'))
                    await command.channel.send(f"Unknown command: `{command.content}`")
                    logger.info(f"Unknown command received: {command.content} from user: {command.author}")
        #
