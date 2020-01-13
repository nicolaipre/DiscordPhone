# -*- coding: utf-8 -*-

"""
Discord API Wrapper
~~~~~~~~~~~~~~~~~~~

A basic wrapper for the Discord API.

:copyright: (c) 2015-2019 Rapptz
:license: MIT, see LICENSE for more details.

"""

__title__ = 'discord'
__author__ = 'Rapptz'
__license__ = 'MIT'
__copyright__ = 'Copyright 2015-2019 Rapptz'
__version__ = '1.3.0a'

from collections import namedtuple
import logging

from .client import Client
from .appinfo import AppInfo
from .user import User, ClientUser, Profile
from .emoji import Emoji
from .partial_emoji import PartialEmoji
from .activity import *
from .channel import *
from .guild import Guild, SystemChannelFlags
from .relationship import Relationship
from .member import Member, VoiceState
from .message import Message, Attachment
from .asset import Asset
from .errors import *
from .calls import CallMessage, GroupCall
from .permissions import Permissions, PermissionOverwrite
from .role import Role
from .file import File
from .colour import Color, Colour
from .invite import Invite, PartialInviteChannel, PartialInviteGuild
from .widget import Widget, WidgetMember, WidgetChannel
from .object import Object
from .reaction import Reaction
from . import utils, opus, abc, rtp
from .enums import *
from .embeds import Embed
from .shard import AutoShardedClient
from .player import *
from .reader import *
from .webhook import *
from .voice_client import VoiceClient
from .audit_logs import AuditLogChanges, AuditLogEntry, AuditLogDiff
from .raw_models import *
from .team import *
from .speakingstate import SpeakingState

VersionInfo = namedtuple('VersionInfo', 'major minor micro releaselevel serial')

version_info = VersionInfo(major=1, minor=3, micro=0, releaselevel='alpha', serial=0)

try:
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

logging.getLogger(__name__).addHandler(NullHandler())

import warnings
warnings.simplefilter('once', category=RuntimeWarning)

warnings.warn("""This is a development branch.

DO NOT:
  - Expect anything to work.
  - Expect anything broken to be fixed in a timely manner.
  - Expect docs.
  - Expect it to be done anytime soon.
  - Expect this code to be up to date with the main repo.
  - Expect help with this fork from randos in the discord.py help channels.
  - Bother people in the help server for assistance anyways.
  - Mention the words "machine learning" or "AI" without being able to
    produce a university email or degree.
  - Try to use this fork without some degree of python competence.
    If I see you struggling with basic stuff I will ignore your problem
    and tell you to learn python.

If you have questions ping Imayhaveborkedit somewhere in the help server and
ask directly.  For other matters such as comments and concerns relating more
to the api design post it here instead:

    https://github.com/Rapptz/discord.py/issues/1094
""", RuntimeWarning, stacklevel=1000)

warnings.simplefilter('default', category=RuntimeWarning)
del warnings
