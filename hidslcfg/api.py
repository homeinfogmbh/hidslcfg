"""Web API client."""

from urllib.parse import urljoin

from requests import ConnectionError, Session   # pylint: disable=W0622

from hidslcfg.exceptions import APIError
from hidslcfg.exceptions import ProgramError


__all__ = ['Client']


LOGIN_URL = 'https://his.homeinfo.de/session'
SETUP_URL_BASE = 'https://termgr.homeinfo.de/setup/'


def get_url(endpoint):
    """Returns a URL for the respective endpoint."""

    return urljoin(SETUP_URL_BASE, endpoint)


class Client:
    """Class to retrieve data from the web API."""

    def __init__(self, user, passwd, system):
        """Initialize with credentials."""
        self.user = user
        self.passwd = passwd
        self.system = system
        self.session = None

    def __enter__(self):
        self.session = Session()
        return self

    def __exit__(self, typ, value, traceback):
        """Handles possible errors."""
        self.session = None

        if isinstance(value, APIError):
            raise ProgramError('WEB API ERROR', str(value))

        if isinstance(value, KeyboardInterrupt):
            print()
            raise ProgramError('Setup aborted by user.')

    def post(self, url, json):
        """Performs a POST request."""
        try:
            response = self.session.post(url, json=json)
        except ConnectionError:
            raise APIError('Cannot connect. Check your internet connection.')

        if response.status_code != 200:
            raise APIError(text=response.text, json=response.json())

        return response

    def login(self):
        """Performs a HIS login."""
        json = {'account': self.user, 'passwd': self.passwd}
        return self.post(LOGIN_URL, json=json)

    @property
    def info(self):
        """Returns the terminal information."""
        url = get_url('info')
        json = {'system': self.system}
        return self.post(url, json).json()

    @property
    def vpndata(self):
        """Returns the terminal's VPN keys and configuration as bytes."""
        url = get_url('openvpn')
        json = {'system': self.system}
        return self.post(url, json).content

    def finalize(self, serial_number=None):
        """Sets the respective serial number."""
        url = get_url('finalize')
        json = {'system': self.system}

        if serial_number is not None:
            json['sn'] = serial_number

        return self.post(url, json).text
