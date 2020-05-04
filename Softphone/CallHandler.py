#!/usr/bin/env python3
# -*- coding: iso-8859-1 -*-
# coding=utf-8

import pjsua as pj
from time import sleep

class CallHandler(pj.CallCallback):
    """ Class to handle callback events from a call. Handles everything that happens within the call.
    """

    def __init__(self, lib, call=None, audio_cb_slot=None):
        pj.CallCallback.__init__(self, call) # Can this be written differently ? the syntax looks dirty... Is it even needed to have? here?
        self.lib = lib
        # self.call = call # fix this.. pj.CallCallback has this thing set...
        self.audio_cb_slot = audio_cb_slot


    def on_state(self):
        """ Notifies when a call state has changed.
        """
        if self.call.info().state == pj.CallState.CONNECTING:
            print('[CallHandler...]: Call is connecting.')

        elif self.call.info().state == pj.CallState.CONFIRMED:
            print("[CallHandler...]: Receiver answered the outgoing call.")

        elif self.call.info().state == pj.CallState.DISCONNECTED:
            print("[CallHandler...]: Call disconnected.")

        #else:
        print("[CallHandler...]: Call with %s is %s. Last code: %s (%s)." % (
            self.call.info().remote_uri,
            self.call.info().state_text,
            self.call.info().last_code,
            self.call.info().last_reason)
        )


    def on_media_state(self):
        """ Notifies when a calls media state has changed.
        """
        if self.call.info().media_state == pj.MediaState.ACTIVE:
            
            # No point connecting these if using null_snd_dev
            self.lib.conf_connect(0, self.call.info().conf_slot) # Move these to on media state.ACTIVE ? https://github.com/malarinv/pjproject/blob/66516e44b9cc9124dd4542002202f6844b05e3b3/pjsip-apps/src/python/samples/audio_cb.py#L66
            self.lib.conf_connect(self.call.info().conf_slot, 0)
            
            # If we are also streaming audio, connect that...
            if self.audio_cb_slot != None:
                self.lib.conf_connect(self.call.info().conf_slot, self.audio_cb_slot)
                self.lib.conf_connect(self.audio_cb_slot, self.call.info().conf_slot)
            
            print("[CallHandler...]: Media is now active.")
        else:
            print("[CallHandler...]: Media is inactive.")


    #def on_transfer_status(self, code, reason, final, cont):
    #def on_transfer_request(self, dst, code):


    # TODO: Add some cool DTMF dial codes here that we can use
    def on_dtmf_digit(self, digits):
        print("[CallHandler...]: Got DTMF digits: %s." % digits)
        pass
    """
        if digits == '#':
            self.wait_for_hash = False
            logging.info("Collected DTMF: %s" % self.collection)
        if self.wait_for_hash:
            self.collection += digits
            return
        if digits == '7':
            self.play_file("../audio/default.wav", enforce_playback=True)
            self.wait_for_hash = True
            self.action = "newcall"
        """

