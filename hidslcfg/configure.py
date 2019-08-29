"""System configuration."""

from time import sleep

from hidslcfg.exceptions import ProgramError
from hidslcfg.globals import LOGGER, UNCONFIGURED_WARNING_SERVICE
from hidslcfg.openvpn import SERVER, unit, install
from hidslcfg.system import hostname
from hidslcfg.system import ping
from hidslcfg.system import reboot
from hidslcfg.system import systemctl
from hidslcfg.system import CalledProcessErrorHandler
from hidslcfg.termio import ask, Table


__all__ = ['confirm', 'configure']


def update_sn(system, serial_number):
    """Updates the serial number hint to indicate changed serial number."""

    if serial_number is not None:
        new_sn = serial_number or None
        current_sn = system.get('serial_number')

        if current_sn is not None:
            new_sn = f'{current_sn} → {new_sn}'

        system['serial_number'] = new_sn

    return system


def warn_deployed(deployment):
    """Warns about possible deployment."""

    if deployment:
        LOGGER.warning('System is already deployed on #%i.', deployment)


def confirm(system, serial_number=None, force=False):
    """Prompt the user to confirm the given location."""

    LOGGER.info('You are about to configure the following system:')
    print(flush=True)
    print(Table.generate(rows(update_sn(system, serial_number))))
    print(flush=True)
    warn_deployed(system.get('deployment'))
    configured = system.get('configured')

    if configured:
        message = f'System has already been configured on {configured}.'

        if not force:
            raise ProgramError(message)

        LOGGER.warning(message)

    if not ask('Is this correct?'):
        raise ProgramError('Setup aborted by user.')


def configure(system, vpn_data, gracetime=3):
    """Performs the system configuration."""

    LOGGER.debug('Installing OpenVPN configuration.')
    install(vpn_data)
    LOGGER.debug('Enabling OpenVPN.')

    with CalledProcessErrorHandler('Enabling of OpenVPN client failed.'):
        systemctl('enable', unit())

    LOGGER.debug('Restarting OpenVPN.')

    with CalledProcessErrorHandler('Restart of OpenVPN client failed.'):
        systemctl('restart', unit())

    LOGGER.debug('Waiting for OpenVPN server to start.')
    sleep(gracetime)
    LOGGER.debug('Checking OpenVPN connection.')

    with CalledProcessErrorHandler('Cannot contact OpenVPN server.'):
        ping(SERVER)

    LOGGER.debug('Configuring host name.')
    hostname(str(system))
    LOGGER.debug('Disabling unconfigured warning.')
    systemctl('disable', UNCONFIGURED_WARNING_SERVICE)
    LOGGER.info('Setup completed successfully.')

    if ask('Do you want to reboot now?'):
        reboot()
    else:
        LOGGER.info('Okay, not rebooting.')


def rows(system):
    """Yields table rows containing system information."""

    yield ('Option', 'Value')   # Header.
    yield ('System ID', system['id'])
    yield ('Creation date', system['created'])
    yield ('Operating system', system['operatingSystem'])
    configured = system.get('configured')

    if configured:
        yield ('Configured', configured)

    serial_number = system.get('serial_number')

    if serial_number:
        yield ('Serial number', serial_number)

    model = system.get('model')

    if model:
        yield ('Model', model)
