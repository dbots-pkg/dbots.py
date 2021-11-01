__title__ = 'dbots'
__author__ = 'Snazzah'
__license__ = 'MIT'
__copyright__ = 'Copyright 2020 Snazzah'
__version__ = '4.0.0'

from collections import namedtuple
import logging

from .http import HTTPClient, HTTPResponse
from .client_filler import *
from .errors import *
from .service import *
from .poster import Poster, ClientPoster, AsyncLoop

VersionInfo = namedtuple(
    'VersionInfo', 'major minor micro releaselevel serial')
version_info = VersionInfo(
    major=4, minor=0, micro=0,
    releaselevel='final', serial=0
)

try:
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

logging.getLogger(__name__).addHandler(NullHandler())
