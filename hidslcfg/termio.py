"""Terminal input and output."""

from enum import Enum
from os import linesep

from hidslcfg.exceptions import ValueMismatch, ProgramError
from hidslcfg.globals import OPTIONS


__all__ = ['ask', 'bold', 'get_serial_number', 'Table']


YES_VALUES = ('y', 'yes')
DEFAULT_SPACING = ' {} '


def ask(question, default=False, yes=YES_VALUES):
    """Ask a question and return True on yes or else False."""

    suffix = ' [Y/n]: ' if default else ' [y/N]: '

    try:
        reply = input(question + suffix)
    except EOFError:
        print()
        return None
    except KeyboardInterrupt:
        print()
        return False

    if not reply:
        return default

    return reply.lower() in yes


def bold(string):
    """Formats a string as bold."""

    return f'\033[1m{string}\033[0m'


def _read_serial_number():
    """Reads the serial number."""

    print('Enter serial number of the device.')
    print('Press [Ctrl]+[D] to skip this step.')

    try:
        serial_number = input('Serial number: ').strip()
        serial_number_confirmation = input('Confirm serial number: ').strip()
    except KeyboardInterrupt:
        print()
        raise ProgramError('Setup aborted by user.')
    except EOFError:
        print()
        print('Skipping setting of serial number.')
        return None

    if serial_number != serial_number_confirmation:
        raise ValueMismatch()

    return serial_number


def get_serial_number():
    """Reads the serial number if configured to do so."""

    try:
        return OPTIONS['serial_number']
    except KeyError:
        if OPTIONS['read_serial_number']:
            try:
                return _read_serial_number()
            except ValueMismatch:
                raise ProgramError('Serial numbers do not match.')

    return None


class Table(Enum):
    """Table elements."""

    THIN = '─'
    BOLD = '═'
    HEADER = '╔{}╦{}╗'
    BOLD_LINE = '╠{}╬{}╣'
    ROW = '║{}║{}║'
    THIN_LINE = '╟{}╫{}╢'
    FOOTER = '╚{}╩{}╝'

    @classmethod
    def make_rows(cls, key_value_pairs, header=True, spacing=DEFAULT_SPACING):
        """Generates rows for a UTF-8 table."""

        items = []
        keys_len = 0
        value_len = 0

        for key, value in key_value_pairs:
            key = spacing.format(key)
            value = spacing.format(value)
            keys_len = max(keys_len, len(key))
            value_len = max(value_len, len(value))
            items.append((key, value))

        yield cls.HEADER.value.format(
            cls.BOLD.value * keys_len, cls.BOLD.value * value_len)

        for row, (key, value) in enumerate(items, start=1):
            key = key.ljust(keys_len)
            value = value.ljust(value_len)

            if header and row == 1:
                yield cls.ROW.value.format(bold(key), bold(value))
                yield cls.BOLD_LINE.value.format(
                    cls.BOLD.value * keys_len, cls.BOLD.value * value_len)
            else:
                yield cls.ROW.value.format(key, value)

                if row < len(items):
                    yield cls.THIN_LINE.value.format(
                        cls.THIN.value * keys_len, cls.THIN.value * value_len)
                else:
                    yield cls.FOOTER.value.format(
                        cls.BOLD.value * keys_len, cls.BOLD.value * value_len)

    @classmethod
    def generate(cls, key_value_pairs, header=True, spacing=DEFAULT_SPACING):
        """Generates a UTF-8 table."""

        return linesep.join(cls.make_rows(
            key_value_pairs, header=header, spacing=spacing))
