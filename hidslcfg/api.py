"""Web API client."""

from json import loads, dumps

from requests import ConnectionError, post

from hidslcfg.exceptions import ProgramError, InvalidCredentials, \
    Unauthorized, APIError

__all__ = ['Client']


class Client:
    """Class to retrieve data from the web API."""

    PROTO = 'https'
    HOST = 'termgr.homeinfo.de'
    PATH = '/setup'

    def __init__(self, user, passwd, cid, tid):
        """Initialize with credentials."""
        self.user = user
        self.passwd = passwd
        self.cid = cid
        self.tid = tid

    def __enter__(self):
        return self

    def __exit__(self, typ, value, traceback):
        """Handles possible errors."""
        if isinstance(value, InvalidCredentials):
            raise ProgramError(
                'INVALID CREDENTIALS',
                'Your user name and / or password are incorrect.')
        elif isinstance(value, Unauthorized):
            raise ProgramError(
                'UNAUTHORIZED',
                'You are not authorized to set up this terminal.')
        elif isinstance(value, APIError):
            raise ProgramError('WEB API ERROR', value)
        elif isinstance(value, KeyboardInterrupt):
            print()
            raise ProgramError('Setup aborted by user.')

    def __call__(self, action, **kwargs):
        """POST to the API with the respective
        user name, password and action call.
        """
        post_data = self.post_data
        post_data.update(kwargs)
        post_data = dumps(post_data).encode()

        try:
            reply = post(self.get_url(action), data=post_data)
        except ConnectionError:
            raise ProgramError(
                'CONNECTION ERROR', 'Check your internet connection.')

        if reply.status_code == 200:
            return reply
        elif reply.status_code == 401:
            if reply.text == 'Invalid credentials':
                raise InvalidCredentials()

            raise Unauthorized()

        raise APIError(reply.text)

    @property
    def post_data(self):
        """Returns the HTTP parameters dictionary."""
        return {
            'userName': self.user,
            'passwd': self.passwd,
            'cid': self.cid,
            'tid': self.tid}

    @property
    def terminal(self):
        """Returns the terminal information."""
        return loads(self('terminal_information').text)

    @property
    def vpndata(self):
        """Returns the terminal's VPN keys and configuration as bytes."""
        return self('vpn_data').content

    def get_url(self, action):
        """Returns the API URL."""
        return f'{self.PROTO}://{self.HOST}{self.PATH}/{action}'

    def set_serial_number(self, serial_number):
        """Sets the respective serial number."""
        return self('serial_number', serial_number=serial_number)
