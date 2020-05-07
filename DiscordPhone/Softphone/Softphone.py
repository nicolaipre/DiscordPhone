#!/usr/bin/env python3
# -*- coding: latin-1 -*-
# Functional inspiration: https://github.com/probonopd/OpenPhone/blob/master/openphone.py

import pjsua as pj
import time

from threading import Thread
from .CallHandler import CallHandler
from .AccountHandler import AccountHandler

class Softphone:

    # Static config options
    ua_cfg = pj.UAConfig()
    log_cfg = pj.LogConfig()
    log_cfg.callback = lambda level, str, len: print('[PJSUA]:', str.strip())
    media_cfg = pj.MediaConfig() # look at the options it takes: https://www.pjsip.org/python/pjsua.htm#MediaConfig


    def __init__(
            self, 
            max_calls=2, 
            nameserver=['1.1.1.1'], 
            user_agent='Python Softphone', 
            log_level=1,
            sample_rate=48000, 
            duration_ms=20,
            channel_count=2,
            max_media_ports=8,
            thread=True
        ):

        # Media config
        self.media_cfg.clock_rate    = sample_rate
        self.media_cfg.channel_count = channel_count 

        #self.media_cfg.snd_clock_rate = sample_rate# Clock rate to be applied when opening the sound device. If value is zero, conference bridge clock rate will be used.
        self.media_cfg.audio_frame_ptime = duration_ms # Discord uses frames containing 20 ms audio data
        #self.media_cfg.no_vad = True # voice activation detection enabled
        #self.media_cfg.enable_ice = False
        self.media_cfg.max_media_ports = max_media_ports

        # User-agent config
        self.ua_cfg.max_calls = max_calls
        self.ua_cfg.nameserver = nameserver
        self.ua_cfg.user_agent = user_agent

        # Log config
        self.log_cfg.level = log_level

        # Lib settings (put this in run() instead when using multiprocessing.Process)
        self.lib = pj.Lib() # Singleton instance
        self.lib.init(ua_cfg=self.ua_cfg, log_cfg=self.log_cfg, media_cfg=self.media_cfg)
        self.lib.start(with_thread=thread)

        # Playback / Recording varaibles
        self.player = None
        self.recorder = None

        # Stream callback id and slot
        self.audio_cb_id   = None
        self.audio_cb_slot = None

        # Call variables
        self.call_handler = True
        self.current_call = None
        print("\n")
        print("[Softphone.....]: Object created.")


    def __del__(self):
        self.lib.destroy()
        print("[Softphone.....]: Object destroyed.")


    def register(self, server, port, username, password, default_account=False, proxy=None, protocol='UDP', bind_address='127.0.0.1', bind_port=0):
        """ Register an account at i.e. Asterisk PBX, and set network transport options.
            Returns: Account registered, account callback handler.
        """
        if   protocol == 'UDP': protocol = pj.TransportType.UDP
        elif protocol == 'TCP': protocol = pj.TransportType.TCP
        elif protocol == 'TLS': protocol = pj.TransportType.TLS
        else: print("[Softphone.....]: Error - Invalid protocol type.")

        print("[Softphone.....]: Creating transport and generating SIP URI.")
        transport = self.lib.create_transport(
            protocol,
            pj.TransportConfig(0) # TransportConfig(host=bind_address, port=bind_port) # TODO: Add bind_address and bind_port here.
        )

        public_sip_uri = "sip:" + username + "@" + str(transport.info().host + ":" + str(transport.info().port))
        print("[Softphone.....]: Listening on %s:%d for %s." % (transport.info().host, transport.info().port, public_sip_uri))
        print("[Softphone.....]: Attempting registration for %s at %s:%s." % (public_sip_uri, server, port) )

        account_cfg = pj.AccountConfig(
            domain   = server + ":" + port,
            username = username,
            password = password
        )

        account_cfg.id = public_sip_uri

        account = self.lib.create_account(acc_config=account_cfg, set_default=default_account)
        account.set_transport(transport)

        account_handler = AccountHandler(lib=self.lib, account=account)
        account.set_callback(account_handler)

        print("[Softphone.....]: Waiting for registration...")
        account_handler.wait()
        print("[Softphone.....]: Successfully registered %s, status: %s (%s)." % (public_sip_uri, account.info().reg_status, account.info().reg_reason))

        return account


    def unregister(self, account):
        """ Unregister a registered account.
        """
        print("[Softphone.....]: Attempting to unregistering account:", account)
        account.delete()
        print("[Softphone.....]: Successfully unregistered account.")


    def call(self, account, sip_uri):
        """ Make a new outgoing call to sip_uri from SIP account.
        """
        try:
            if self.current_call:
                print("[Softphone.....]: Already have a call.")
                return

            if self.lib.verify_sip_url(sip_uri) != 0:
                print("[Softphone.....]: Invalid SIP URI.")
                return

            print("[AccountHandler]: Attempting new call to %s" % sip_uri)
            lck = self.lib.auto_lock() # To prevent deadlocks
            call_handler = CallHandler(lib=self.lib, audio_cb_slot=self.audio_cb_slot)
            self.current_call = account.make_call(sip_uri, cb=call_handler)
            print('[Softphone.....]: Current call is %s.' % self.current_call)
            del lck

        except pj.Error as e:
            print("[Softphone.....]: Error -", e)
            self.current_call = None
            self.lib.destroy()


    def end_call(self):
        """ Hang up an ongoing call for SIP account.
        """
        try:
            if not self.current_call:
                print("[Softphone.....]: There is no call.")
                return

            self.current_call.hangup()
            self.current_call = None
            print("[Softphone.....]: Call ended.")

        except pj.Error as e:
            print("[Softphone.....]: Error -", e)


    def wait_for_active_audio(self):
        """ Wait until call audio is activated.
        """
        while self.current_call.info().media_state != pj.MediaState.ACTIVE:
            time.sleep(0.5)


    def get_sound_devices(self):
        """ Get a detailed list of available sound devices.
            Returns a list of available sound devices.
        """
        sounddevices = []

        snd_devs = self.lib.enum_snd_dev()

        i = 0
        for snd_dev in snd_devs:
            dev = {}
            dev['index'] = i
            dev['name'] = snd_dev.name
            dev['input_channels'] = snd_dev.input_channels
            dev['output_channels'] = snd_dev.output_channels
            dev['sample_rate'] = snd_dev.default_clock_rate
            sounddevices.append(dev)
            i+=1

        return sounddevices


    def set_null_sound_device(self):
        """ Set NULL sound device / Do not use system audio device.
        """
        self.lib.set_null_snd_dev()
        print('[Softphone.....]: Using NULL sound device.')


    def get_capture_device(self):
        """ Get capture device ID currently in use.
        """
        capture_id, playback_id = self.lib.get_snd_dev()
        return capture_id


    def set_capture_device(self, capture_id):
        """ Set capture device ID to be used.
        """
        _, playback_id = self.lib.get_snd_dev()
        self.lib.set_snd_dev(capture_id, playback_id)
        print("[Softphone.....]: Capture device set to:", capture_id)


    def get_playback_device(self):
        """ Get playback device ID currently in use.
        """
        capture_id, playback_id = self.lib.get_snd_dev()
        return playback_id


    def set_playback_device(self, playback_id):
        """ Set playback device ID to be used.
        """
        capture_id, _ = self.lib.get_snd_dev()
        self.lib.set_snd_dev(capture_id, playback_id)
        print("[Softphone.....]: Playback device set to:", playback_id)


    def capture(self, file_name):
        """ Save call audio to WAV file.
        """
        self.recorder = self.lib.create_recorder(file_name)
        recorder_slot = self.lib.recorder_get_slot(self.recorder)
        self.lib.conf_connect(recorder_slot, self.current_call.info().conf_slot) 
        self.lib.conf_connect(self.current_call.info().conf_slot, recorder_slot)
        print("[Softphone.....]: Started audio capture.")


    def stop_capturing(self):
        """ Stop capturing call audio to file
        """
        self.lib.recorder_destroy(self.recorder)
        self.recorder = None
        print("[Softphone.....]: Stopped audio capture.")


    def playback(self, file_name):
        """ Playback a WAV file into call.
        """
        self.player = self.lib.create_player(file_name)
        player_slot = self.lib.player_get_slot(self.player)
        self.lib.conf_connect(player_slot, self.current_call.info().conf_slot)
        print("[Softphone.....]: Started audio playback.")


    def stop_playback(self):
        """ Stop playing audio file to call
        """
        self.lib.player_destroy(self.player)
        self.player = None
        print("[Softphone.....]: Stopped audio playback.")


    def create_audio_stream(self, audio_callback):
        self.audio_cb_id   = self.lib.create_audio_cb(audio_callback)
        self.audio_cb_slot = self.lib.audio_cb_get_slot(self.audio_cb_id)
        print("[Softphone.....]: Created audio callback.")


    def destroy_audio_stream(self):
        self.lib.audio_cb_destroy(self.audio_cb_id)
        self.audio_cb_id = None
        self.audio_cb_slot = None
        print("[Softphone.....]: Destroyed audio callback.")
