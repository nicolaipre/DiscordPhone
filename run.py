#!/usr/bin/env python3
# -*- coding: latin-1 -*-

import argparse
import configparser
import logging
from DiscordPhone.DiscordPhone import DiscordPhone

# Initialize logging # TODO: Fix full logging
logging.basicConfig(
    filename='run.log',
    filemode='a',
    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
    datefmt='%H:%M:%S',
    level=logging.DEBUG
)
#self.logger = logging.getLogger('urbanGUI')

# Parse CLI arguments # TODO: Check if config file exists
parser = argparse.ArgumentParser()
parser.add_argument("-c", "--config", help="Config file to use", required=True)
parser.parse_args()
args = parser.parse_args()

# Read specified config
config = configparser.ConfigParser()
config.read(args.config)

# Run
logging.info(f"Starting DiscordPhone with config {args.config}")
client = DiscordPhone(config)
client.run(config['DISCORD']['token'])
