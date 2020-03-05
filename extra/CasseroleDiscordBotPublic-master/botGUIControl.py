from tkinter import Tk, Label, Button, StringVar
import threading
import asyncio
import time, math


class CasseroleDiscordBotGUI(threading.Thread):
    def __init__(self, discordConnRef):

        self.discordConnRef = discordConnRef

        threading.Thread.__init__(self)

    def run(self):

        self.master = Tk()
        self.master.title("Casserole Discord Bot")

        self.statusText = StringVar()
        self.statusLabel = Label(self.master , textvariable=self.statusText)
        self.statusLabel.pack()

        #self.spanishButton = Button(self.master , text="In Spanish", command=self.setSpanish)
        #self.spanishButton.pack()

        #self.englishButton = Button(self.master , text="In English", command=self.setEnglish)
        #self.englishButton.pack()

        self.voiceConnectButton = Button(self.master , text="Voice Connect", command=self.onVoiceConnect, background='green')
        self.voiceConnectButton.pack()

        self.voiceHangUpButton = Button(self.master , text="Hang Up", command=self.onHangUp, background='red')
        self.voiceHangUpButton.pack()

        self.close_button = Button(self.master , text="Close", command=self.onClose)
        self.close_button.pack()

        self.master.protocol("WM_DELETE_WINDOW", self.onClose)


        # Kick off background GUI updates
        self.master.after(300,self.periodicGUIUpdate)

        # run main app
        self.master.mainloop()


    # GUI Callbacks
    def setSpanish(self):
        self.discordConnRef.message = "¡Hola, amigo!"
        print("Switched to Spanish")

    def setEnglish(self):
        self.discordConnRef.message = "Hello, friend!"
        print("Switched to English")

    def onVoiceConnect(self):
        self.discordConnRef.connectRequest = True

    def onHangUp(self):
        self.discordConnRef.connectRequest = False


    def onClose(self):
        print("Disconnecting from Discord...")
        self.discordConnRef.shutdownRequest = True
        print("All done. CasseroleBot says goodnight!")
        self.master.quit()

    def periodicGUIUpdate(self):
        message = ""

        if(self.discordConnRef.isLoggedIn == False):
            message = "Logging In..."
        else:
            message = "Ready to place call"

        if(self.discordConnRef.connectRequest):
            if(self.discordConnRef.isConnected):
                message = "Call in Process. \n Speaker: {}".format(self.discordConnRef.speakingUserString)
            else:
                message = "Connecting to voice channel..."
        else:
            if(self.discordConnRef.isConnected):
                message = "Hanging up..."

        
        self.statusText.set(message)
        #repeat evert 250ms
        self.master.after(250, self.periodicGUIUpdate)
