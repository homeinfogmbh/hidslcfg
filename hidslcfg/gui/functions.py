"""Helper functions."""

from pathlib import Path


__all__ = ['get_xml']


def get_xml(filename: str) -> Path:
    """Returns the path to an XML GUI file."""

    return Path(__file__).parent / 'xml' / filename
