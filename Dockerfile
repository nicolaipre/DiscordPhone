FROM ubuntu:18.04
LABEL maintainer="skandix@datapor.no"

# Lets start with getting the time correct
ENV TZ=Europe/Oslo
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Try to avoid cache while testing
ARG CACHEBUST=1|

# TODO: Add for better sec.
# RUN useradd --create-home discordphone
# WORKDIR /home/discordphone
# USER discordphone

# Install Packages from APT !
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-dev \
    build-essential \
    wget \
    unzip \
    git \
    libasound2-dev \
    libportaudio2 \
    libopus0 \
    libsodium23 \
    libffi-dev \
    ffmpeg \
    ca-certificates \
    musl-dev

# Important to use py37, if not audio streaming will not be supported
RUN wget https://github.com/DiscordPhone/pjproject/archive/py37.zip \
    -O py37.zip  && \
    unzip py37.zip && \
    cd pjproject-py37 && \
    chmod +x configure aconfigure && \
    ./configure CXXFLAGS=-fPIC CFLAGS=-fPIC LDFLAGS=-fPIC CPPFLAGS=-fPIC && \
    make clean && \
    make dep && \
    make && \
    make install && \
    cd pjsip-apps/src/python && \
    python3 setup.py build && \
    python3 setup.py install


# Upgrade pip and ensure we have what we need
RUN pip3 install --upgrade pip setuptools wheel

# Clone softphone repo
RUN wget https://github.com/DiscordPhone/softphone/archive/master.zip -O softphone.zip

RUN unzip softphone.zip

RUN pip3 install -e softphone-master

# Copy stuff into image
COPY . .

# Install pip dependencies
RUN pip3 install --no-cache-dir -r requirements.txt
#    pip3 install --upgrade --force-reinstall --version websockets==4.0.1 # Why?

# Install discord.py (fork by: imayhaveborkedit) - No longer needed, since this is imported in the "discord" folder.
# RUN pip3 install --no-cache-dir setuptools && \
#     pip3 install --no-cache-dir https://github.com/imayhaveborkedit/discord.py/archive/voice-recv-mk2.zip

# Remove packages that are not used in runtime, to try lower image size
RUN apt purge -y \
    python3-pip \
    wget \
    unzip \
    build-essential

# To keep down the size of the image, clean out that cache when finished installing packages.
RUN apt-get clean -y && \
    apt-get autoclean -y && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get autoremove -y

# docker run
CMD ["python3", "run.py"]
