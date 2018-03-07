"""System configuration."""

from contextlib import suppress
from time import sleep

from hidslcfg.exceptions import ProgramError
from hidslcfg.globals import UNCONFIGURED_WARNING_SERVICE, OPTIONS
from hidslcfg.openvpn import SERVER, unit, install
from hidslcfg.system import systemctl, ping, hostname, reboot, \
    CalledProcessErrorHandler
from hidslcfg.termio import ask, bold, Table

__all__ = ['confirm_terminal', 'configure']


NO_REBOOT_MSG = '''Okay, not rebooting.'
You can reboot any time by pressing
[CTRL]+[ALT]+[DEL]'''


def update_sn(dictionary, serial_number):
    """Updates the serial number hint to indicate changed serial number."""

    if serial_number is not None:
        new_sn = serial_number or None
        current_sn = dictionary.get('serial_number')

        if current_sn is not None:
            new_sn = f'{current_sn} → {new_sn}'

        dictionary['serial_number'] = new_sn

    return dictionary


def confirm_terminal(dictionary, serial_number=None):
    """Prompt the user to confirm the given location."""

    print(bold('You are about to configure the following terminal:'))
    print()
    print(Table.generate(rows(update_sn(dictionary, serial_number))))
    print()

    if not ask('Is this correct?'):
        raise ProgramError('Setup aborted by user.')


def configure(tid, cid, vpn_data, gracetime=3):
    """Performs the terminal configuration."""

    verbose = OPTIONS['verbose']

    if verbose:
        print('Installing OpenVPN configuration.')

    install(vpn_data)

    if verbose:
        print('Enabling OpenVPN.')

    with CalledProcessErrorHandler('Enabling of OpenVPN client failed.'):
        systemctl('enable', unit())

    if verbose:
        print('Restarting OpenVPN.')

    with CalledProcessErrorHandler('Restart of OpenVPN client failed.'):
        systemctl('restart', unit())

    if verbose:
        print('Waiting for OpenVPN server to start.')

    sleep(gracetime)

    if verbose:
        print('Checking OpenVPN connection.')

    with CalledProcessErrorHandler('Cannot contact OpenVPN server.'):
        ping(SERVER)

    if verbose:
        print('Configuring host name.')

    hostname(f'{tid}.{cid}')

    if verbose:
        print('Disabling on-screen warning.')

    with CalledProcessErrorHandler('Disabling of on-screen warning failed.'):
        systemctl('disable', UNCONFIGURED_WARNING_SERVICE)

    print()
    print('Setup completed successfully.')

    if ask('Do you want to reboot now?'):
        reboot()
    else:
        print(NO_REBOOT_MSG)


def rows(dictionary):
    """Yields table rows containing terminal information."""

    yield ('Option', 'Value')   # Header.
    yield ('TID', dictionary['tid'])

    try:
        cid = dictionary['customer']['cid']
    except KeyError:
        yield ('Customer', dictionary['customer'])
    else:
        try:
            company = dictionary['customer']['company']['name']
        except KeyError:
            yield ('Customer', cid)
        else:
            yield ('Customer', f'{company} ({cid})')

    try:
        location = dictionary['location']
    except KeyError:
        yield ('Location', '!!!Not configured!!!')
    else:
        address = location['address']

        with suppress(KeyError):
            yield ('Street', address['street'])

        with suppress(KeyError):
            yield ('House number', address['house_number'])

        with suppress(KeyError):
            yield ('ZIP code', address['zip_code'])

        with suppress(KeyError):
            yield ('City', address['city'])

        with suppress(KeyError):
            yield ('Annotation', location['annotation'])

    yield ('Scheduled', dictionary.get('scheduled', 'Not scheduled.'))
    yield ('Deployed', dictionary.get('deployed', 'Not deployed.'))
    yield ('Serial number', dictionary.get('serial_number'))
