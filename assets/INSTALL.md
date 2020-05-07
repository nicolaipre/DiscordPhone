# Installation instructions for DiscordPhone
Follow the instructions below to successfully set up your instance of DiscordPhone.
- You will also need a SIP Trunk provider for the SIP configuration.
- The SIP Trunk provider must allow custom caller ID for spoofing to work.

## Install pjsua (patch by: malarinv)
```sh=
sudo apt install python3 python3-dev build-essential libasound2-dev
wget https://github.com/nicolaipre/pjproject/archive/py37.zip
unzip py37.zip
cd pjproject-py37
chmod +x configure aconfigure
./configure CXXFLAGS=-fPIC CFLAGS=-fPIC LDFLAGS=-fPIC CPPFLAGS=-fPIC
make dep
make
sudo make install
cd pjsip-apps/src/python
python3 setup.py build
sudo python3 setup.py install
```

## Install discord.py (fork by: imayhaveborkedit)
```sh=
python3 -m pip install https://github.com/imayhaveborkedit/discord.py/archive/voice-recv-mk2.zip
```

## Edit Asterisk configuration files
Adjust the following config files to your liking. See `assets/asterisk/*.conf` for examples.
- /etc/asterisk/sip.conf
- /etc/asterisk/extensions.conf
- /etc/asterisk/manager.conf
- /etc/asterisk/manager.d/admin.conf

## Restart or reload Asterisk
This must be done after configuration files have been updated.
- `sudo service asterisk restart`
- `sudo service asterisk reload`