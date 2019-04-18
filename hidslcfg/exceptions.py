"""Exceptions used by hidslcfg."""

__all__ = [
    'ProgramError',
    'InvalidCredentials',
    'Unauthorized',
    'APIError']


class ProgramError(Exception):
    """Indicates an error in the program."""

    def __init__(self, error, *messages, sep=' ', exit_code=2):
        """Prints error messages to stderr and exit."""
        super().__init__(error, *messages)
        self.error = error
        self.messages = messages
        self.sep = sep
        self.exit_code = exit_code

    def __str__(self):
        """Returns the respective string."""
        return f'\033[91m\033[1m{self.error}\033[0m {self.message}'

    @property
    def message(self):
        """Returns the respective message text."""
        return self.sep.join(str(message) for message in self.messages)


class InvalidCredentials(Exception):
    """Indicates invalid credentials."""


class Unauthorized(Exception):
    """Indicates that the user is not allowed
    to setup the respective terminal.
    """


class APIError(Exception):
    """Indicates an error while using the web API."""
