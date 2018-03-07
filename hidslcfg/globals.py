"""Global constants and configuration."""

from pathlib import Path


__all__ = [
    'UNCONFIGURED_WARNING_SERVICE',
    'APPLICATION_SERVICE',
    'DIGSIG_DATA_DIR',
    'OPTIONS']


UNCONFIGURED_WARNING_SERVICE = 'unconfigured-warning.service'
APPLICATION_SERVICE = 'application.service'
DIGSIG_DATA_DIR = Path('/usr/share/digsig')
OPTIONS = {'verbose': False, 'gracetime': 3}
