"""Basic system configuration."""

from hidslcfg.exceptions import ProgramError
from hidslcfg.globals import LOGGER, UNCONFIGURED_WARNING_SERVICE
from hidslcfg.system import hostname
from hidslcfg.system import systemctl
from hidslcfg.termio import ask, Table


__all__ = ['confirm', 'configure']


def update_sn(system, serial_number):
    """Updates the serial number hint to indicate changed serial number."""

    if serial_number is not None:
        new_sn = serial_number or None

        if (current_sn := system.get('serial_number')) is not None:
            new_sn = f'{current_sn} → {new_sn}'

        system['serial_number'] = new_sn

    return system


def confirm(system, serial_number=None, force=False):
    """Prompt the user to confirm the given location."""

    LOGGER.info('You are about to configure the following system:')
    print(flush=True)
    print(Table.generate(rows(update_sn(system, serial_number))))
    print(flush=True)

    if deployment := system.get('deployment'):
        LOGGER.warning('System is already deployed on #%i.', deployment)

    if configured := system.get('configured'):
        message = f'System has already been configured on {configured}.'

        if not force:
            raise ProgramError(message)

        LOGGER.warning(message)

    if not ask('Is this correct?'):
        raise ProgramError('Setup aborted by user.')


def configure(system):
    """Performs the system configuration."""

    LOGGER.debug('Configuring host name.')
    hostname(str(system))
    LOGGER.debug('Disabling unconfigured warning.')
    systemctl('disable', UNCONFIGURED_WARNING_SERVICE)


def rows(system):
    """Yields table rows containing system information."""

    yield ('Option', 'Value')   # Header.
    yield ('System ID', system['id'])
    yield ('Creation date', system['created'])
    yield ('Operating system', system['operatingSystem'])

    if configured := system.get('configured'):
        yield ('Configured', configured)

    if serial_number := system.get('serialNumber'):
        yield ('Serial number', serial_number)

    if model := system.get('model'):
        yield ('Model', model)
