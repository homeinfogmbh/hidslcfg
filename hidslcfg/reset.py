"""Reset operations."""

from functools import partial
from subprocess import CalledProcessError
from typing import Callable, NamedTuple

from hidslcfg.common import APPLICATION_SERVICE
from hidslcfg.common import DIGSIG_DATA_DIR
from hidslcfg.common import UNCONFIGURED_WARNING_SERVICE
from hidslcfg.exceptions import ProgramError
from hidslcfg.openvpn import DEFAULT_SERVICE, clean
from hidslcfg.system import systemctl, hostname, rmsubtree
from hidslcfg.wireguard import remove


__all__ = ['reset']


class ResetOperation(NamedTuple):
    """A reset operation."""

    description: str
    function: Callable


# Oder matters here!
RESET_OPERATIONS = (
    ResetOperation('reset hostname', partial(hostname, None)),
    ResetOperation(
        'remove digital signage data',
        partial(rmsubtree, DIGSIG_DATA_DIR)
    ),
    ResetOperation(
        'disable OpenVPN service',
        partial(systemctl, 'disable', DEFAULT_SERVICE)
    ),
    ResetOperation('Removing OpenVPN configuration', clean),
    ResetOperation('remove WireGuard configuration', remove),
    ResetOperation(
        'disable application',
        partial(systemctl, 'disable', APPLICATION_SERVICE)
    ),
    ResetOperation(
        'disable application',
        partial(systemctl, 'enable', UNCONFIGURED_WARNING_SERVICE)
    )
)


def reset():
    """Resets the system's configuration."""

    for description, function in RESET_OPERATIONS:
        try:
            function()
        except CalledProcessError:
            raise ProgramError(f'Could not {description}.')
