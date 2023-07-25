"""Terminal input and output."""

from enum import Enum
from getpass import getpass
from os import linesep
from typing import Iterator, Iterable

from hidslcfg.exceptions import ProgramError


__all__ = ["ask", "bold", "read_credentials", "Table"]


YES_VALUES = {"y", "yes"}
DEFAULT_SPACING = " {} "


def ask(question: str, default: bool = False) -> bool | None:
    """Ask a question and return True on yes or else False."""

    suffix = " [Y/n]: " if default else " [y/N]: "

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

    return reply.strip().lower() in YES_VALUES


def bold(string: str) -> str:
    """Formats a string as bold."""

    return f"\033[1m{string}\033[0m"


def read_credentials(user: str) -> tuple[str, str]:
    """Reads the username."""

    try:
        if user is None:
            user = input("User name: ")

        passwd = getpass("Password: ")
    except EOFError:
        print()
        raise ProgramError("Missing mandatory data.") from None
    except KeyboardInterrupt:
        print()
        raise ProgramError("Configuration aborted by user.") from None

    return user, passwd


class Table(Enum):
    """Table elements."""

    THIN = "─"
    BOLD = "═"
    HEADER = "╔{}╦{}╗"
    BOLD_LINE = "╠{}╬{}╣"
    ROW = "║{}║{}║"
    THIN_LINE = "╟{}╫{}╢"
    FOOTER = "╚{}╩{}╝"

    @classmethod
    def make_rows(
        cls,
        key_value_pairs: Iterable[tuple[str, str]],
        header: bool = True,
        spacing: str = DEFAULT_SPACING,
    ) -> Iterator[str]:
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
            cls.BOLD.value * keys_len, cls.BOLD.value * value_len
        )

        for row, (key, value) in enumerate(items, start=1):
            key = key.ljust(keys_len)
            value = value.ljust(value_len)

            if header and row == 1:
                yield cls.ROW.value.format(bold(key), bold(value))
                yield cls.BOLD_LINE.value.format(
                    cls.BOLD.value * keys_len, cls.BOLD.value * value_len
                )
            else:
                yield cls.ROW.value.format(key, value)

                if row < len(items):
                    yield cls.THIN_LINE.value.format(
                        cls.THIN.value * keys_len, cls.THIN.value * value_len
                    )
                else:
                    yield cls.FOOTER.value.format(
                        cls.BOLD.value * keys_len, cls.BOLD.value * value_len
                    )

    @classmethod
    def generate(
        cls,
        key_value_pairs: Iterable[tuple[str, str]],
        header: bool = True,
        spacing: str = DEFAULT_SPACING,
    ) -> str:
        """Generates a UTF-8 table."""
        rows = cls.make_rows(key_value_pairs, header=header, spacing=spacing)
        return linesep.join(rows)
