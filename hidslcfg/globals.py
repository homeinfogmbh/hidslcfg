"""Global constants and configuration."""

from pathlib import Path


__all__ = ['APPLICATION_SERVICE', 'DIGSIG_DATA_DIR', 'OPTIONS']


APPLICATION_SERVICE = 'application.service'
DIGSIG_DATA_DIR = Path('/usr/share/digsig')
OPTIONS = {'verbose': False}
