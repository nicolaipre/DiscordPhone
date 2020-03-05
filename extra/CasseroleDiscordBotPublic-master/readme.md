## Casserole Discord Bot

Work In Process

![Casserole](/casserole.jpeg)

This repo contains source code and utilities for the teleconference phone hardware, which is utilized by a Discord bot to act like a conference room phone.

The hardware involves a Raspberry Pi 3b (which we had lying around), and a Revolabs 1500 IP phone (which we got used on ebay).

If you're looking around here, a few big things to keep in mind:

### Python Libraries

Uses the [Discord Python API](https://github.com/Rapptz/discord.py) and a handful of other things through a python virtualenv. See requirements.txt for more details.

NOTE: In order to get audio streaming working effectively, I had to pull not the main discord.py, but made a local copy of [github user imayhaveborkedit](https://github.com/imayhaveborkedit)'s [fork of discord.py](https://github.com/imayhaveborkedit/discord.py). [Details about their changes are on this RFC.](https://github.com/Rapptz/discord.py/issues/1094). Basically, new API's for voice client `listen()` and supporting classes were added to make incoming audio data available. Forward this on to the speakers, and we're golden! Despite the developmental nature of the library, seems to be quite stable and happy at the moment?

### Revolabs FLX Interface

I have exactly zero documentation for this device. The contents of that interface were all reverse engineered by looking at the bits that came across the linux kernel generic HID USB device streams. It's a hack if I ever saw one. It only works on Linux. It was the result of trying to solve a problem the easy way, which happened to be the hard way, but I learned stuff in the process anyway.

Alternate: use GPIO pins on the Raspberry Pi. We may try to do this at some point. Just not yet.

### Sudo

The script calls `sudo` in the middle. It's yucky. I am sorry. Make sure you run this as a user who can `sudo`.

### Secret Keys

We keep our API keys in a python file in a different directory, outside this repo. Change lines in `casseroelBot.py` or `theBlueAlliance.py` with your own API keys for Discord and TBA respectively. 

### Setup

Assuming your on some Debian (or Raspian) similar distro:

Copy or hardlink casseroleBot.service to somewhere systemd can see it.

Start & enable it.

Again, totally WIP.
