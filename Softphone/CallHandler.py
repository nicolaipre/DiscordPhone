#!/usr/bin/env python3
# -*- coding: iso-8859-1 -*-
# coding=utf-8

import pjsuaxt as pj
from time import sleep

class CallHandler(pj.CallCallback):
    """ Class to handle callback events from a call. Handles everything that happens within the call.
    """

    def __init__(self, lib, call=None):
        pj.CallCallback.__init__(self, call)    # Can this be written differently ? the syntax looks dirty..
        self.lib = lib


    def on_state(self):
        """ Notifies when a call state has changed.
        """

        if self.call.info().state == pj.CallState.CONNECTING:
            print('[CallHandler]: Call is connecting.')

        elif self.call.info().state == pj.CallState.CONFIRMED:
            print("[CallHandler]: Receiver answered the outgoing call.")

            # This is what you would do to connect system audio:
            self.lib.conf_connect(0, self.call.info().conf_slot)
            self.lib.conf_connect(self.call.info().conf_slot, 0)
            # The best thing would probably be to hook all audio up here,
            # since we know the call state is confirmed. However, we do
            # it in functions in softphone instead.

        elif self.call.info().state == pj.CallState.DISCONNECTED:
            print('[CallHandler]: Call disconnected.')

        #else:
        print("[CallHandler]: Call with %s is %s. Last code: %s (%s)." % (
            self.call.info().remote_uri,
            self.call.info().state_text,
            self.call.info().last_code,
            self.call.info().last_reason)
        )


    def on_media_state(self):
        """ Notifies when a calls media state has changed.
        """

        if self.call.info().media_state == pj.MediaState.ACTIVE:
            print("[CallHandler]: Media is now active.")
        else:
            print("[CallHandler]: Media is inactive.")


    #def on_transfer_status(self, code, reason, final, cont):
    #def on_transfer_request(self, dst, code):


    # TODO: Add some cool DTMF dial codes here that we can use
    def on_dtmf_digit(self, digits):
        print("[CallHandler]: Got DTMF digits: %s." % digits)
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

