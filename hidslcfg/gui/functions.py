"""Helper functions."""

from pathlib import Path


__all__ = ['get_asset']


def get_asset(filename: str) -> Path:
    """Returns the path to an asset file."""

    return Path(__file__).parent / 'assets' / filename
