
import sys
import pjsua as pj
from time import sleep
from AccountHandler import AccountHandler

class SIPPhone():

    # User-agent config
    ua_cfg = pj.UAConfig()
    ua_cfg.max_calls = 10
    ua_cfg.nameserver = ["1.1.1.1"]
    ua_cfg.user_agent = "DiscordPhone"

    # Log config
    log_cfg = pj.LogConfig()
    log_cfg.level = 1
    log_cfg.callback = lambda level, str, len: print(str.strip())

    # Media config
    media_cfg = pj.MediaConfig()
    media_cfg.channel_count = 8
    media_cfg.max_media_ports = 8


    def __init__(self, config):
        self.lib = pj.Lib()
        self.lib.init(ua_cfg   =self.ua_cfg,
                      log_cfg  =self.log_cfg,
                      media_cfg=self.media_cfg)
        self.lib.start(with_thread=True)

        # Account information
        self.outboundCallAccount, self.outboundAccountHandler, self.outboundCallConfig = self.register(config, default=True)  # Register the account once we load the SIPPhone class.. (outbound)
        #self.self.inboundCallAccount, self.inboundAccountHandler, self.inboundCallConfig = self.register(calling)  # TODO: Register for inbound calls.

        self.currentCall = None # Holds the current call
        self.callHandler = None

    #endDef


    def register(self, config, default=False):

        # Transport registration
        print("[+] Creating transport and generating SIP URI")
        transport = self.lib.create_transport(pj.TransportType.UDP, pj.TransportConfig(port=9999)) # Can add bind address here
        SIP_URI = "sip:" + config['username'] + "@" + str(transport.info().host + ":" + str(transport.info().port)) # Comment out this line if you have a uri in DiscordPhone.conf
        print("[+] Listening on %s:%d for %s" % (transport.info().host, transport.info().port, SIP_URI))


        # Account registration
        print("[+] Attempting registration for %s at %s:%s" % (SIP_URI, config['server'], config['port']) )
        account_cfg = pj.AccountConfig(domain  =config['server'] + ":" + config['port'], 
                                       username=config['username'],
                                       password=config['secret'],
                                       proxy   =config['proxy'])
        account_cfg.id = SIP_URI

        account = self.lib.create_account(acc_config=account_cfg,
                                          set_default=default)
        account.set_transport(transport)

        accountHandler = AccountHandler(lib=self.lib, account=account)
        account.set_callback(accountHandler)
        accountHandler.wait()
        print("[+] %s registered, status: %s (%s)" % (SIP_URI, account.info().reg_status, account.info().reg_reason))

        return (account, accountHandler, account_cfg)

    #endDef


    def endCall(self):
        try:
            if not self.currentCall:
                print("[!] There is no call")
                return
            self.currentCall.hangup()
            self.currentCall = None # reset the variable

        except pj.Error as e:
            print("[!] Exception: " + str(e))
            self.outboundCallAccount.delete()
            self.lib.destroy()



    def initiateCall(self, dst_sip_uri):
        try:
            if self.currentCall:
                print("[!] Already have another call")
                return

            if self.lib.verify_sip_url(dst_sip_uri) != 0: # See documentatoon for verify_sip_url (returns 0 if valid)
                print("[!] Invalid SIP URI")
                return

            lck = self.lib.auto_lock()
            self.currentCall, self.callHandler = self.outboundAccountHandler.new_call(dst_sip_uri)
            print('[+] Current call is', self.currentCall)
            del lck

        except pj.Error as e:
            print("[!] Exception: " + str(e))
            self.outboundCallAccount.delete()
            self.lib.destroy()



    def destroy(self):
        self.outboundCallAccount.delete()
        self.lib.destroy()
