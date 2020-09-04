"""Web API client."""

from urllib.parse import urljoin

from requests import ConnectionError, Session   # pylint: disable=W0622

from hidslcfg.exceptions import APIError, ProgramError


__all__ = ['Client']


LOGIN_URL = 'https://his.homeinfo.de/session'
SETUP_URL_BASE = 'https://termgr.homeinfo.de/setup/'


def get_url(endpoint: str) -> str:
    """Returns a URL for the respective endpoint."""

    return urljoin(SETUP_URL_BASE, endpoint)


class Client:
    """Class to retrieve data from the web API."""

    def __init__(self, user: str, passwd: str, system: int):
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

    def post(self, url: str, json: dict):
        """Performs a POST request."""
        try:
            response = self.session.post(url, json=json)
        except ConnectionError:
            raise APIError('Connection error. Check your internet connection.')

        if response.status_code != 200:
            raise APIError.from_response(response)

        return response

    def login(self):
        """Performs a HIS login."""
        json = {'account': self.user, 'passwd': self.passwd}
        return self.post(LOGIN_URL, json=json)

    def post_endpoint(self, endpoint: str):
        """Makes a POST request to the respective endpoint."""
        return self.post(get_url(endpoint), {'system': self.system})

    @property
    def info(self) -> dict:
        """Returns the terminal information."""
        return self.post_endpoint('info').json()

    @property
    def openvpn(self) -> bytes:
        """Returns the terminal's VPN keys and configuration as bytes."""
        return self.post_endpoint('openvpn').content

    @property
    def wireguard(self) -> dict:
        """Returns the terminal's WireGuard configuration."""
        return self.post_endpoint('wireguard').json()

    def finalize(self, **json) -> str:
        """Sets the respective serial number."""
        json['system'] = self.system
        return self.post(get_url('finalize'), json).text
