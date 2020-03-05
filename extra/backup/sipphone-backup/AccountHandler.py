
import threading
import pjsua as pj
# https://github.com/probonopd/OpenPhone/blob/master/openphone.py - good. rip from this
from CallHandler import CallHandler

# This class handles everything that prepares for, and accepts calls (Before CallHandler) - remember, we hit the Account first, then we establish the call, and handle call with CallHandler.
class AccountHandler(pj.AccountCallback):

    sem = None

    def __init__(self, lib, account=None):
        self.lib = lib #pj.Lib().instance()  # Singleton
        self.lib.set_null_snd_dev() # disable sound device
        #self.lib.set_snd_dev(1, 1)
        #self.lib.set_snd_dev(2, 2)  # SET SOUND DEVICES HERE !!!!!!!! (int capture_dev_id, playback_dev_id)
        snd_dev = lib.get_snd_dev()
        print(snd_dev)
        pj.AccountCallback.__init__(self, account)  # Can this be written differently ? looks dirty..
    #endDef


    def wait(self):
        self.sem = threading.Semaphore(0)
        self.sem.acquire()
    #endDef


    def on_reg_state(self):
        print("[+] Reg state: %s" % str(self.account.info().reg_status))
        if self.sem:
            if self.account.info().reg_status >= 200:
                self.sem.release()
    #endDef


    def on_incoming_call(self, call):
        print("Call recieved: %s" % call)

        # TODO: Fix this..
        """
        if current_call:
            call.answer(486, "Busy")
            return

        print("[+] Incoming call from ", call.info().remote_uri)
        print("[+] Press 'a' to answer")
        """
        
        callHandler = CallHandler(lib=self.lib, call=call)
        callHandler.setAccount(self)
        call.answer(180) # why 180?
        call.set_callback(callHandler)

        # Connect to call slot to sound device..
        self.lib.conf_connect(call.info().conf_slot, 0)
        self.lib.conf_connect(0, call.info().conf_slot)
    #endDef


    def new_call(self, uri, connectSlot=None):
        print("[+] Attempting new call to %s" % uri)

        try:
            callHandler = CallHandler(lib=self.lib)
            callHandler.setAccount(self)
            call = self.account.make_call(uri, cb=callHandler)

            if connectSlot:
                while call.info().media_state != pj.MediaState.ACTIVE:
                    # self.lib.handle_events()
                    sleep(0.5)
                    continue

                self.lib.conf_connect(connectSlot, call.info().conf_slot) # (0, call)
                self.lib.conf_connect(call.info().conf_slot, connectSlot) # (call, 0)

            return (call, callHandler)

        except pj.Error as e:
            print("Exception: " + str(e))
            return None
    #endDef


#endClass
