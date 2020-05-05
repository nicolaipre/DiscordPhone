
# Dependency installation instructions for DiscordPhone

## Install pjsuaxt (mod by: nicolaipre)
```sh
sudo apt install python3 python3-dev build-essential libasound2-dev
wget https://www.pjsip.org/release/2.9/pjproject-2.9.zip
unzip pjproject-2.9.zip
cd pjproject-2.9
chmod +x configure aconfigure
./configure CXXFLAGS=-fPIC CFLAGS=-fPIC LDFLAGS=-fPIC CPPFLAGS=-fPIC
make dep
make
sudo make install

cd pjsip-apps/src/
git clone https://github.com/nicolaipre/python3-pjsip-memory-buffer.git
cd python3-pjsip-memory-buffer

python3 setup-pjsuaxt.py build
sudo python3 setup-pjsuaxt.py install
```


## Install `discord.py` (fork by: imayhaveborkedit)
```sh
wget https://github.com/imayhaveborkedit/discord.py/archive/voice-recv-mk2.zip
unzip voice-recv-mk2.zip
cd voice-recv-mk2
python3 setup.py install
```

## Clone Softphone repo
git clone git@github.com:nicolaipre/Softphone.git

