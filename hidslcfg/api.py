"""Web API client."""

from enum import Enum
from typing import Callable
from urllib.parse import urljoin

from requests import ConnectionError as ConnErr, Response, Session

from hidslcfg.exceptions import APIError, ProgramError


__all__ = ['Client']


LOGIN_URL = 'https://his.homeinfo.de/session'
SETUP_URL_BASE = 'https://termgr.homeinfo.de/setup/'


class HTTPMethod(Enum):
    """Available HTTP methods."""

    POST = 'POST'
    PATCH = 'PATCH'


class Client:
    """Class to retrieve data from the web API."""

    def __init__(self):
        """Initialize with credentials."""
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

    def get_http_method(self, method: HTTPMethod) -> Callable:
        """Returns the requested HTTP method to call."""
        if method is HTTPMethod.POST:
            return self.session.post

        if method is HTTPMethod.PATCH:
            return self.session.patch

        raise NotImplementedError(f'HTTP method {method} is not implemented.')

    def request(self, method: HTTPMethod, url: str, json: dict) -> Response:
        """Make a request."""
        try:
            response = self.get_http_method(method)(url, json=json)
        except ConnErr:
            raise APIError('Connection error.') from None

        if response.status_code != 200:
            raise APIError.from_response(response)

        return response

    def post(self, url: str, json: dict) -> Response:
        """Performs a POST request."""
        return self.request(HTTPMethod.POST, url, json)

    def patch(self, url: str, json: dict) -> Response:
        """Performs a PATCH request."""
        return self.request(HTTPMethod.PATCH, url, json)

    def login(self, account: str, passwd: str) -> Response:
        """Performs a HIS login."""
        return self.post(LOGIN_URL, {'account': account, 'passwd': passwd})

    def post_endpoint(self, endpoint: str, **json) -> Response:
        """Makes a POST request to the respective endpoint."""
        return self.post(urljoin(SETUP_URL_BASE, endpoint), json)

    def info(self, system: int) -> dict:
        """Returns the terminal information."""
        return self.post_endpoint('info', system=system).json()

    def openvpn(self, system: int) -> bytes:
        """Returns the terminal's VPN keys and configuration as bytes."""
        return self.post_endpoint('openvpn', system=system).content

    def finalize(self, **json) -> str:
        """Sets the respective serial number."""
        return self.post_endpoint('finalize', **json).text

    def add_system(self, **json) -> dict:
        """Adds a new WireGuard system."""
        return self.post(urljoin(SETUP_URL_BASE, 'system'), json).json()

    def patch_system(self, **json) -> dict:
        """Patches an existing WireGuard system."""
        return self.patch(urljoin(SETUP_URL_BASE, 'system'), json).json()
