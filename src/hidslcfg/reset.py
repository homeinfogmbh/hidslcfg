"""Reset operations."""

from functools import partial
from subprocess import CalledProcessError

from hidslcfg.exceptions import ProgramError
from hidslcfg.globals import UNCONFIGURED_WARNING_SERVICE, \
    APPLICATION_SERVICE, DIGSIG_DATA_DIR
from hidslcfg.openvpn import unit, clean
from hidslcfg.system import systemctl, hostname, rmsubtree


RESET_OPS = (
    ('reset hostname', partial(hostname, None)),
    ('remove digital signage data', partial(rmsubtree, DIGSIG_DATA_DIR)),
    ('disable OpenVPN service', partial(systemctl, 'disable', unit())),
    ('Removing OpenVPN configuration', clean),
    ('disable application',
     partial(systemctl, 'disable', APPLICATION_SERVICE)),
    ('enable on-screen warning',
     partial(systemctl, 'enable', UNCONFIGURED_WARNING_SERVICE)))


def reset():
    """Resets the system's configuration."""

    for operation, function in RESET_OPS:
        try:
            function()
        except CalledProcessError:
            raise ProgramError(f'Could not {operation}.')
