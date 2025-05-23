"""Global constants and configuration."""

from argparse import Namespace
from logging import DEBUG, INFO, basicConfig, getLogger
from os import getenv, geteuid
from pathlib import Path
from sys import argv
from typing import Callable

from hidslcfg.exceptions import ProgramError


__all__ = [
    "APPLICATION_SERVICE",
    "CHROMIUM_SERVICE",
    "DDB_OS_PKG_NAME",
    "DDBOSSTART",
    "DDBOSSTART_TEMPLATE",
    "DIGSIG_DATA_DIR",
    "HIDSL_DEBUG",
    "HTML5DS",
    "INSTALLATION_INSTRUCTIONS_SERVICE",
    "LOGGER",
    "LOG_FORMAT",
    "SYSTEMD_NETWORKD",
    "SYSTEMD_NETWORK_DIR",
    "UNCONFIGURED_WARNING_SERVICE",
    "init_root_script",
]


APPLICATION_SERVICE = "application.service"
CHROMIUM_SERVICE = "chromium.service"
DDB_OS_PKG_NAME = "ddb-os"
DIGSIG_DATA_DIR = Path("/var/lib/digsig")
HIDSL_DEBUG = getenv("HIDSL_DEBUG")
HTML5DS = "html5ds.service"
INSTALLATION_INSTRUCTIONS_SERVICE = "installation-instructions.service"
LOG_FORMAT = "[%(levelname)s] %(name)s: %(message)s"
LOGGER = getLogger(Path(argv[0]).name)
SYSTEMD_NETWORKD = "systemd-networkd.service"
SYSTEMD_NETWORK_DIR = Path("/etc/systemd/network")
UNCONFIGURED_WARNING_SERVICE = "unconfigured-warning.service"
DDBOSSTART_TEMPLATE = Path("/usr/share/hidslcfg/index.html.template")
DDBOSSTART = Path("/srv/index.html")

def init_root_script(args_getter: Callable) -> Namespace:
    """Initializes a script that shall be run as root."""

    args = args_getter()
    basicConfig(level=DEBUG if args.verbose else INFO, format=LOG_FORMAT)

    if geteuid() != 0:
        raise ProgramError("You need to be root to run this script!")

    return args
