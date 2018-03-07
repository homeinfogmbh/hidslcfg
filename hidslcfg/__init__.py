"""HOMEINFO Digital Signage Linux configurator."""

from hidslcfg.api import Client
from hidslcfg.configure import confirm_terminal, configure
from hidslcfg.globals import OPTIONS
from hidslcfg.reset import reset


__all__ = ['OPTIONS', 'confirm_terminal', 'configure', 'reset', 'Client']
