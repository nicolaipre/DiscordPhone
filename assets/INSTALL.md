# Installation instructions
Follow the instructions below to successfully set up your instance of DiscordPhone.

## Prerequisites
- You will also need a SIP Trunk provider for the SIP configuration.
- The SIP Trunk provider must allow custom caller ID for spoofing to work.

## Install discord.py (fork by: imayhaveborkedit)
```bash
python3 -m pip install https://github.com/imayhaveborkedit/discord.py/archive/voice-recv-mk2.zip
```

## Install Asterisk
```bash
sudo apt install asterisk -y
```

### Edit Asterisk configuration files
Adjust the following config files to your liking. See `assets/asterisk/*.conf` for examples.
- /etc/asterisk/sip.conf
- /etc/asterisk/extensions.conf
- /etc/asterisk/manager.conf
- /etc/asterisk/manager.d/admin.conf

### Restart or reload Asterisk
This must be done after configuration files have been updated.
- `sudo service asterisk restart`
- `sudo service asterisk reload`
