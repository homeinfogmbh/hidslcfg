"""Basic system configuration."""

from ipaddress import IPv4Address, IPv6Address
from typing import Any, Iterable

from hidslcfg.common import (
    INSTALLATION_INSTRUCTIONS_SERVICE,
    LOGGER,
    UNCONFIGURED_WARNING_SERVICE,
    DDBOSSTART_TEMPLATE,
    DDBOSSTART
)
from hidslcfg.exceptions import ProgramError
from hidslcfg.hosts import set_ip
from hidslcfg.pacman import set_server
from hidslcfg.system import set_hostname, systemctl
from hidslcfg.termio import ask, Table
from hidslcfg.system import get_system_id, is_ddb_os_system

from pathlib import Path

__all__ = ["confirm", "configure","create_ddbos_start"]


APPCMD_HOSTNAME = "appcmd.homeinfo.intra"


def update_sn(system: dict, serial_number: str) -> dict:
    """Updates the serial number hint to indicate changed serial number."""

    if serial_number is not None:
        new_sn = serial_number or None

        if (current_sn := system.get("serial_number")) is not None:
            new_sn = f"{current_sn} → {new_sn}"

        system["serial_number"] = new_sn

    return system


def rows(system: dict) -> Iterable[tuple[str, Any]]:
    """Yields table rows containing system information."""

    yield "Option", "Value"  # Header.
    yield "System ID", system["id"]
    yield "Creation date", system["created"]
    yield "Operating system", system["operatingSystem"]

    if configured := system.get("configured"):
        yield "Configured", configured

    if serial_number := system.get("serialNumber"):
        yield "Serial number", serial_number

    if model := system.get("model"):
        yield "Model", model


def confirm(system: dict, serial_number: str = None, force: bool = False) -> None:
    """Prompt the user to confirm the given location."""

    LOGGER.info("You are about to configure the following system:")
    print(flush=True)
    print(Table.generate(rows(update_sn(system, serial_number))))
    print(flush=True)

    if deployment := system.get("deployment"):
        LOGGER.warning("System is already deployed on #%i.", deployment)

    if configured := system.get("configured"):
        message = f"System has already been configured on {configured}."

        if not force:
            raise ProgramError(message)

        LOGGER.warning(message)

    if not ask("Is this correct?"):
        raise ProgramError("Setup aborted by user.")


def configure(system: int, server: IPv4Address | IPv6Address) -> None:
    """Configures the system with the given ID."""

    LOGGER.debug("Configuring host name.")
    set_hostname(str(system))
    LOGGER.debug("Updating /etc/hosts.")
    set_ip(APPCMD_HOSTNAME, server)
    LOGGER.debug("Updating /etc/pacman.conf.")
    set_server("homeinfo", server)
    LOGGER.debug("Disabling unconfigured warning.")
    systemctl("disable", UNCONFIGURED_WARNING_SERVICE)
    systemctl("enable", INSTALLATION_INSTRUCTIONS_SERVICE)
    create_ddbos_start()
def create_ddbos_start()->None:
    if is_ddb_os_system():
        system=get_system_id()
        with DDBOSSTART_TEMPLATE.open(encoding="utf-8") as file:
            start_template = file.read()
        start_template = start_template.format(system=system)
        with DDBOSSTART.open(mode="w", encoding="utf-8") as indexfile:
            indexfile.write(start_template)
