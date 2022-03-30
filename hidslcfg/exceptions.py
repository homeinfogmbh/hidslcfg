"""Exceptions used by hidslcfg."""

from contextlib import suppress
from json import JSONDecodeError
from os import linesep


__all__ = ['APIError', 'ProgramError']


class APIError(Exception):
    """Indicates an error while using the web API."""

    def __init__(self, text: str | None = None, json: dict | None = None):
        """Sets the raw error message text and / or JSON."""
        super().__init__()
        self.text = text
        self.json = json

    def __str__(self):
        """Returns the respective message text."""
        if self.json:
            with suppress(TypeError, KeyError):
                return self.json['message']

        return self.text

    @classmethod
    def from_response(cls, response):
        """Returns an API error from a response."""
        try:
            json = response.json()
        except JSONDecodeError:
            json = None

        return cls(text=response.text, json=json)


class ProgramError(Exception):
    """Indicates an error in the program."""

    def __init__(self, error: str, *messages: str, exit_code: int = 2):
        """Prints error messages to stderr and exit."""
        super().__init__(error, *messages)
        self.error = error
        self.messages = messages
        self.exit_code = exit_code

    def __str__(self):
        """Returns the respective message text."""
        return linesep.join(str(message) for message in self.messages)
