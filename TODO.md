# TODO

- [ ] Fix when mobile hangs up before Discord
- [ ] Add Nexmo, cellsynt or ClockworkSMS API for sms
- [ ] enable incoming calls + get phone number for discord
- [ ] replace prints with python logger
- [ ] check if callerID(name()) works
- [ ] Improve blacklist.json + matching
- [x] Check that specified config file exists

- [ ] Add Mic + Speakers for testing so we dont have to call every time we test the Discord Part, since phone works good now.
- [ ] Test by setting Python threads = 1 in pjsip library (see if it helps with delay)
- [ ] Make a separate repository for pjsip-softphone, and move softphone out.
- [ ] Add mic/speaker source/sink for discordphone and softphone and test which one has delay.
- [ ] Make blacklist.json

## Not prioritized
- [ ] Add better command handler with prefix etc..: https://stackoverflow.com/q/59126137
- [ ] https://github.com/CorentinJ/Real-Time-Voice-Cloning
