"""Global constants and configuration."""

from logging import getLogger
from pathlib import Path
from sys import argv


__all__ = [
    'APPLICATION_SERVICE',
    'DIGSIG_DATA_DIR',
    'LOGGER',
    'LOG_FORMAT',
    'UNCONFIGURED_WARNING_SERVICE']


APPLICATION_SERVICE = 'application.service'
DIGSIG_DATA_DIR = Path('/usr/share/digsig')
LOG_FORMAT = '[%(levelname)s] %(name)s: %(message)s'
LOGGER = getLogger(Path(argv[0]).name)
UNCONFIGURED_WARNING_SERVICE = 'unconfigured-warning.service'
