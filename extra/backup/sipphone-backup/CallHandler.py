
import pjsua as pj

from time import sleep


# This class handles everything that happens within the call
class CallHandler(pj.CallCallback):

    def __init__(self, lib, call=None):
        self.lib     = lib #pj.Lib().instance()  # Singleton
        self.account = None
        pj.CallCallback.__init__(self, call)    # Can this be written differently ? the syntax looks dirty..
    #endDef


    def setAccount(self, account):
        self.account = account
    #endDef


    def getAccount(self):
        return self.account
    #endDef


    def on_state(self):
        if self.call.info().state == pj.CallState.DISCONNECTED:
            print('[+] Call disconnected')

        elif self.call.info().state == pj.CallState.CONNECTING:
            print("asdasd")

        elif self.call.info().state == pj.CallState.CONFIRMED:
            # Connect audio here...
            print("[+] Receiver answered the outgoing call!")

        else:
            print("[+] Call with %s is %s. Last code: %s (%s)" % (self.call.info().remote_uri,
                                                              self.call.info().state_text,
                                                              self.call.info().last_code,
                                                              self.call.info().last_reason))
    #endDef

        
    def on_media_state(self):
        if self.call.info().media_state == pj.MediaState.ACTIVE:
            print("[+] Media is now active")
            
            call_slot = self.call.info().conf_slot
            self.lib.conf_connect(0, call_slot)  # Connect sound device/mic to call
            self.lib.conf_connect(call_slot, 0)  # Connect call to sound device/speaker    

        else:
            print("[+] Media is inactive")
    #endDef


    # TODO: Add some cool DTMF dial codes here that we can use ;) 
    def on_dtmf_digit(self, digits):
        print("[+] Got DTMF digit: %s" % digits)
        pass
        """
        if digits == '#':
            self.wait_for_hash = False
            logging.info("Collected DTMF: %s" % self.collection)
            if self.action == "newcall":
                self.account.new_call(self.collection, self.call.info().conf_slot)
        if self.wait_for_hash:
            self.collection += digits
            return
        if digits == '7':
            self.play_file("../audio/default.wav", enforce_playback=True)
            self.wait_for_hash = True
            self.action = "newcall"
        """
    #endDef


#endClass
