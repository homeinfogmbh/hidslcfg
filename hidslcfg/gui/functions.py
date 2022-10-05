"""Helper functions."""

from pathlib import Path

from hidslcfg.common import HIDSL_DEBUG


__all__ = ['get_asset']


ASSETS_DIR = Path('/usr/share/hidslcfg')


def get_asset(filename: str) -> Path:
    """Return the path to an asset file."""

    return get_base_dir() / filename


def get_base_dir() -> Path:
    """Return the assets base directory."""

    if HIDSL_DEBUG:
        return Path(__file__).parent / 'assets'

    return ASSETS_DIR
