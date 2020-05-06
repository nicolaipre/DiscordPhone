
# Installation instructions for DiscordPhone

## Install pjsua (patch by: malarinv)
```sh
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

## Install `discord.py` (fork by: imayhaveborkedit)
```sh
python3 -m pip install https://github.com/imayhaveborkedit/discord.py/archive/voice-recv-mk2.zip
```