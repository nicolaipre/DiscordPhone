import discord
from tkinter import Tk, Label, Button, StringVar
import threading
import asyncio
import time, math, random
import sounddevice as sd
from audioHandling import *
from botGUIControl import *
from cheerHandler import *
from theBlueAlliance import *
from revolabsFLXInterface import *

from markovChainGen.posify import *
import markovify

import os,sys, re
sys.path.append("..")
import APIKeys


helpStr = " Hi {}! I'm the Casserole Discord Bot! \n" \
          " Be sure to @ mention me if you want to talk. \n" \
          " I know a few cheers which I'll respond to. \n" \
          " I also function as a conference phone (still WIP). \n\n" \
          " The phone is controlled with the following commands: \n" \
          "   `callin` - Causes me to call into the Team Meetings channel \n" \
          "   `callinmentor` - Causes me to call into the Mentor Meetings channel \n" \
          "   `hangup` - Causes me to leave the Team Meetings channel \n" \
          "   `hold`   - Toggles whether I broadcast the microphone, or some spiffy on-hold music. \n\n" \
          " I'm hooked into the Blue Alliance for fun and profit. Ask me things like: \n" \
          "   `who is <team number>` - I'll look up the team name. \n\n" \
          " There are a few system utilities:\n" \
          "   `reboot` - Causes my host computer to turn off and back on again. \n\n" \
          " Play around and have some fun! Talk to programming team if you want me to learn to do new things. \n" \
          " If I don't know what you're saying, I'll just say something that sounds like I know something about robotics. \n" \


# What channel should the phone connect to?
PHONE_TEAM_VOICE_CHANNEL_NAME = 'Team Meetings'
PHONE_MENTOR_VOICE_CHANNEL_NAME = 'Mentor Meetings'


# Actual discord API. This is what does the heavy lifting
class CasseroleDiscordBotClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        #Because team spirit is a real award:
        self.cheer = CheerHandler()
        #And becuase looking up stuff on the TBA is fun
        self.tbaInfo = TBAInfo()

        #self.audioSource = TestAudioSource()
        print("Creating audio Sources & Sinks...")
        self.mikeAudioSource = MicrophoneAudioSource()
        self.holdAudioSource1 = WaveFileAudioSource('./hold1.wav')
        self.holdAudioSource2 = WaveFileAudioSource('./hold2.wav')
        self.audioSink = SpeakerAudioSink()
        #self.audioSink   = NullAudioSink()
        self.buttonsInterface = RevolabsFLXInterface()
        print("Audio hardware setup complete!")

        print("Loading Markov Chat data...")
        self.markovModel = None
        with open("./markovChainGen/CDmarkovModel.json") as f:
            text = f.read()
            self.markovModel = POSifiedText.from_json(text)
        print("Markov Chat init completed!")
        
        self.voiceClient = None
        self.curVoiceChannel = ""

        self.systemRebootRequested = False

        #Inputs from the outside world - changing these will change the Client state
        self.connectRequest = False
        self.shutdownRequest = False
        self.holdRequest = False

        #Outputs to the rest of the world - other classes should read these
        self.speakingUserString = "..."

        self.isLoggedIn= False
        self.isConnected= False
        self.connectRequestPrev = False
        self.holdRequestPrev = False

        self.callBtnPressCntPrev = 0
        self.muteBtnPressCntPrev = 0

        # Trigger a periodic loop to update the Client state based on GUI inputs
        self.loop.create_task(self.periodicStateCheck())

    async def voiceConnectTeam(self):
        await self._voiceConnect(PHONE_TEAM_VOICE_CHANNEL_NAME)

    async def voiceConnectMentor(self):
        await self._voiceConnect(PHONE_MENTOR_VOICE_CHANNEL_NAME)

    # Initiates the Audio Connection
    async def _voiceConnect(self, channelName):
        if(self.voiceClient == None):
            print("Attempting to connect to voice channel {}".format(channelName))
            channel = discord.utils.get(client.get_all_channels(), name=channelName)
            self.voiceClient = await channel.connect()
            self.voiceClient.play(self.mikeAudioSource)
            self.voiceClient.listen(self.audioSink)
            self.isConnected = True
            self.holdRequest = False
            self.holdRequestPrev = False
            self.curVoiceChannel = channelName
            print("Connected!")

    # Starts on-hold music
    async def enableHold(self):
        if(self.voiceClient is not None):
            try:
                self.voiceClient.stop()
                self.voiceClient.stop_listening()
            except Exception as e:
                print(e)
            time.sleep(0.5)
            if(bool(random.getrandbits(1))):
                self.voiceClient.play(self.holdAudioSource1)
            else:
                self.voiceClient.play(self.holdAudioSource2)


    # Starts on-hold music
    async def disableHold(self):
        if(self.voiceClient is not None):
            try:
                self.voiceClient.stop()
            except Exception as e:
                print(e)
            time.sleep(0.5)
            self.voiceClient.play(self.mikeAudioSource)
            self.voiceClient.listen(self.audioSink)


    # Ends the Audio Connection
    async def hangUp(self):
        if(self.voiceClient is not None):
            print("Attempting to hang up from voice channel {}".format(self.curVoiceChannel))
            try:
                self.voiceClient.stop()
                self.voiceClient.stop_listening()
            except Exception as e:
                print(e)
            time.sleep(1.0)
            await self.voiceClient.disconnect()
            self.voiceClient = None
            self.isConnected = False
            self.curVoiceChannel = ""
            print("Disconnected!")

    # Hook to capture Discord Login Event
    async def on_ready(self):
        print('Logged in to Discord as {} - ID {}'.format(self.user.name, self.user.id))
        print('Ready to recieve commands!')
        self.isLoggedIn = True
        

    # Hook to process incoming text from any channel
    async def on_message(self, message):
        if message.author == self.user:
            return

        # check bot was mentioned in the message
        processText = False
        for user in  message.mentions:
            if(self.user.id == user.id):
                processText = True
                break

        messageText = message.content.lower().strip()

        if(processText):
            # Strip out the mention token from the message prior to parsing
            messageText = message.content.lower().strip()
            messageText = re.sub(r'\<\@[0-9]+\>', ' ', messageText)
            
        messageText = messageText.strip()

        # Also respond if the message starts with a dollar sign
        if(messageText.startswith("$")):
            processText = True
            messageText = messageText[1:]
            messageText = messageText.strip()

        # Chime in on cheering for things
        if("yay" in messageText):
            processText = True
        
        if(processText):

            response = ""
            reboot_requested = False

            await message.channel.trigger_typing()

            cheerResponse = self.cheer.update(messageText)
            if(len(cheerResponse) > 0):
                response = cheerResponse

            # Handle phone commands
            elif messageText.startswith('callinmentor'):
                print("Connect Command from {}".format(message.author))
                await self.voiceConnectMentor()
                response = "Connected to Mentor Voice Channel!"

            elif messageText.startswith('callin'):
                print("Connect Command from {}".format(message.author))
                await self.voiceConnectTeam()
                response = "Connected to Team Voice Channel!"

            elif messageText.startswith('hangup'):
                print("Disconnect Command from {}".format(message.author))
                await self.hangUp()
                response = "Goodbye!"

            elif messageText.startswith('hold'):
                print("Hold State Change Command from {}".format(message.author))
                self.holdRequest = not(self.holdRequest)
                if(self.holdRequest):
                    response = "Holding. Enjoy the music!"
                else:
                    response = "Microphones live!"

            # Handle various system commands
            elif messageText.startswith('help'):
                print("Help request {}".format(message.author))
                response = helpStr.format(message.author)

            elif messageText.startswith('reboot'):
                print("Reboot command from {}".format(message.author))
                await self.voiceConnectTeam()
                response = "Attempting to turn myself on and off again!"
                reboot_requested = True

            else:
                # Handle some lookup commands
                results = re.search("\who is ([0-9]+)", messageText)
                if(results):
                    lookupStr = results.group(1).strip()
                    try:
                        teamNum = int(lookupStr)
                        response = "Team {} is '{}'".format(teamNum, self.tbaInfo.lookupTeamName(teamNum))
                    except Exception as e:
                        print(e)
                        response = "Sorry, not sure who team '{}' is.".format(lookupStr)
                else:
                    #No other command written, so just print some technical phrases.
                    response = self.markovModel.make_short_sentence(300)
                    if(response is None):
                        # Markov assembly failed. Well then. Ummm.
                        response = "Did you ever hear the tragedy of Darth Plagueis The Wise? I thought not. It's not a story the Jedi would tell you. It's a Sith legend. Darth Plagueis was a Dark Lord of the Sith, so powerful and so wise he could use the Force to influence the midichlorians to create life… He had such a knowledge of the dark side that he could even keep the ones he cared about from dying. The dark side of the Force is a pathway to many abilities some consider to be unnatural. He became so powerful… the only thing he was afraid of was losing his power, which eventually, of course, he did. Unfortunately, he taught his apprentice everything he knew, then his apprentice killed him in his sleep. Ironic. He could save others from death, but not himself."
                    
            await message.channel.send(response)

            self.systemRebootRequested = reboot_requested



    # Main periodic loop 
    async def periodicStateCheck(self):
        while(True):
            if(self.isLoggedIn):    
                #Only run updates if we're connected

                #Handle inputs from the physical speaker
                if(self.buttonsInterface.callBtnPressCount != self.callBtnPressCntPrev):
                    self.callBtnPressCntPrev = self.buttonsInterface.callBtnPressCount
                    self.connectRequest = not(self.connectRequest)

                if(self.buttonsInterface.muteBtnPressCount != self.muteBtnPressCntPrev):
                    self.muteBtnPressCntPrev = self.buttonsInterface.muteBtnPressCount
                    self.holdRequest = self.buttonsInterface.phoneMute


                #Check if connection request has changed
                if(self.connectRequest != self.connectRequestPrev):
                    #Call or hang up as needed
                    print("Connection request changed to {}".format(self.connectRequest))
                    if(self.connectRequest):
                        await self.voiceConnectTeam()
                    else:
                        await self.hangUp()
                    self.connectRequestPrev = self.connectRequest

                #Check if hold request has changed
                if(self.holdRequest != self.holdRequestPrev):
                    print("Hold request changed to {}".format(self.holdRequest))
                    if(self.holdRequest == True):
                        await self.enableHold()
                    else:
                        await self.disableHold()
                    self.holdRequestPrev = self.holdRequest

                #Update LED State
                # print("hold: {} | connect: {}".format(self.holdRequest, self.connectRequest))
                # if(self.holdRequest == True or self.connectRequest == False):
                #     self.buttonsInterface.setLedsMuted()
                # else:
                #     print("here")
                #     self.buttonsInterface.setLedsUnmuted()

                # Update the string representing the curretly-speaking user
                if(self.connectRequest == True ):
                    member = self.guilds[0].get_member(self.audioSink.curSpeakerID)
                    if(member is not None):
                        if member.nick is not None:
                            self.speakingUserString = str(member.nick)
                        else:
                            self.speakingUserString = str(member)
                else:
                    self.speakingUserString = "..."

                # Check if we're supposed to exit from the program
                if(self.shutdownRequest == True):
                    print("Exiting...")
                    await self.shutDown()
                    return
                
                # Check if we're supposed to reboot the whole system
                if(self.systemRebootRequested):
                    print("Exiting and rebooting...")
                    os.system("sudo reboot")
                    while(True):
                        pass #await powerdown

            # Allow other stuff to run
            await asyncio.sleep(0.25)


    async def shutDown(self):
        await self.logout()


#############################################
## Main code execution starts here
if __name__ == "__main__":
    client = CasseroleDiscordBotClient()
    #gui = CasseroleDiscordBotGUI(client) #temp, no gui for now.
    #gui.start()
    print("Starting up Casserole Discord Bot....")
    client.run(APIKeys.DISCORD_CLIENT_BOT_KEY)


