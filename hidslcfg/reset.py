"""Reset operations."""

from functools import partial
from subprocess import CalledProcessError
from typing import Callable, NamedTuple

from hidslcfg.common import APPLICATION_SERVICE
from hidslcfg.common import CHROMIUM_SERVICE
from hidslcfg.common import DIGSIG_DATA_DIR
from hidslcfg.common import HTML5DS
from hidslcfg.common import UNCONFIGURED_WARNING_SERVICE
from hidslcfg.exceptions import ProgramError
from hidslcfg.openvpn.common import DEFAULT_SERVICE
from hidslcfg.openvpn.disable import clean
from hidslcfg.system import systemctl, set_hostname, rmsubtree
from hidslcfg.wireguard.disable import remove


__all__ = ["reset"]


class ResetOperation(NamedTuple):
    """A reset operation."""

    description: str
    function: Callable


def gracefully_disable_service(service: str) -> None:
    """Disables a service."""

    try:
        systemctl("disable", service)
    except CalledProcessError as cpe:
        if cpe.returncode != 1:
            raise


# Oder matters here!
RESET_OPERATIONS = (
    ResetOperation("reset hostname", partial(set_hostname, "unconfigured")),
    ResetOperation("remove digital signage data", partial(rmsubtree, DIGSIG_DATA_DIR)),
    ResetOperation(
        "disable OpenVPN service", partial(systemctl, "disable", DEFAULT_SERVICE)
    ),
    ResetOperation("remove OpenVPN configuration", clean),
    ResetOperation("remove WireGuard configuration", remove),
    ResetOperation(
        "disable application", partial(gracefully_disable_service, APPLICATION_SERVICE)
    ),
    ResetOperation(
        "disable chromium", partial(gracefully_disable_service, CHROMIUM_SERVICE)
    ),
    ResetOperation("disable html5ds", partial(gracefully_disable_service, HTML5DS)),
    ResetOperation(
        "enable not-configured warning message",
        partial(systemctl, "enable", UNCONFIGURED_WARNING_SERVICE),
    ),
)


def reset() -> None:
    """Resets the system's configuration."""

    for description, function in RESET_OPERATIONS:
        try:
            function()
        except CalledProcessError:
            raise ProgramError(f"Could not {description}.") from None
