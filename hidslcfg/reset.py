"""Reset operations."""

from collections import namedtuple
from functools import partial
from subprocess import CalledProcessError

from hidslcfg.exceptions import ProgramError
from hidslcfg.globals import APPLICATION_SERVICE
from hidslcfg.globals import DIGSIG_DATA_DIR
from hidslcfg.globals import UNCONFIGURED_WARNING_SERVICE
from hidslcfg.openvpn import unit, clean
from hidslcfg.system import systemctl, hostname, rmsubtree


__all__ = ['reset']


ResetOperation = namedtuple('ResetOperation', ('description', 'function'))


RESET_OPERATIONS = (
    ResetOperation('reset hostname', partial(hostname, None)),
    ResetOperation(
        'remove digital signage data', partial(rmsubtree, DIGSIG_DATA_DIR)),
    ResetOperation(
        'disable OpenVPN service', partial(systemctl, 'disable', unit())),
    ResetOperation('Removing OpenVPN configuration', clean),
    ResetOperation(
        'disable application',
        partial(systemctl, 'disable', APPLICATION_SERVICE)),
    ResetOperation(
        'disable application',
        partial(systemctl, 'enable', UNCONFIGURED_WARNING_SERVICE)))


def reset():
    """Resets the system's configuration."""

    for description, function in RESET_OPERATIONS:
        try:
            function()
        except CalledProcessError:
            raise ProgramError(f'Could not {description}.')
