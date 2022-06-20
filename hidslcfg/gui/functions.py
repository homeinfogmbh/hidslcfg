"""Helper functions."""

from pathlib import Path


__all__ = ['get_asset']


ASSETS_DIR = Path('/usr/share/hidslcfg')


def get_asset(filename: str) -> Path:
    """Returns the path to an asset file."""

    return get_base_dir() / filename


def get_base_dir() -> Path:
    """Return the assets base directory."""

    if ASSETS_DIR.is_dir():
        return ASSETS_DIR

    return Path(__file__).parent / 'assets'
