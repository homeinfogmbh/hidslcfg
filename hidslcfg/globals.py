"""Global constants and configuration."""

from logging import getLogger
from pathlib import Path
from sys import argv


__all__ = ['APPLICATION_SERVICE', 'DIGSIG_DATA_DIR', 'LOGGER', 'LOG_FORMAT']


APPLICATION_SERVICE = 'application.service'
DIGSIG_DATA_DIR = Path('/usr/share/digsig')
LOG_FORMAT = '[%(levelname)s] %(name)s: %(message)s'
LOGGER = getLogger(argv[0])
