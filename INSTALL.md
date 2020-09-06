# Installation
Follow the instructions below to set up DiscordPhone without Docker.

---
## Dependencies
- https://github.com/DiscordPhone/softphone
- https://github.com/DiscordPhone/AsteriskPBX
- https://github.com/imayhaveborkedit/discord.py
- https://github.com/DiscordPhone/pjproject/tree/py37

---
## Install discord.py (fork by: imayhaveborkedit) - Not needed anymopre since we have "discord" folder in repo.
```bash
python3 -m pip install https://github.com/imayhaveborkedit/discord.py/archive/voice-recv-mk2.zip
```

---
## Fix audio alsa buffer underruns / audio errors
In `/etc/pulse/daemon.conf` set:
```
default-sample-rate = 48000
default-fragments = 5
default-fragment-size-msec = 2
```
Then restart PulseAudio with
```bash
pulseaudio -k
```