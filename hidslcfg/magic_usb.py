"""Magic USB key with configuration."""

from pathlib import Path
from subprocess import CompletedProcess, run
from tempfile import TemporaryDirectory


__all__ = ["MagicUSBKey"]


LABEL = "DDBCFG"
SEARCH_DIR = Path("/dev/disk/by-label")


class MagicUSBKey:
    """Context manager to mount and umount the USB stick."""

    def __init__(self, *, label: str = LABEL):
        self._device: Path = SEARCH_DIR / label
        self._temporary_directory: TemporaryDirectory | None = None
        self._mountpoint: str | None = None

    def __enter__(self) -> Path:
        self._temporary_directory = TemporaryDirectory()
        self._mountpoint = self._temporary_directory.__enter__()
        mount(self._device, self._mountpoint)
        return self.mountpoint

    def __exit__(self, typ, value, traceback):
        umount(self._mountpoint)
        self._mountpoint = None
        return self._temporary_directory.__exit__(typ, value, traceback)

    @property
    def mountpoint(self) -> Path:
        """Return the path to the mount point."""
        return Path(self._mountpoint)


def mount(device: str | Path, mountpoint: str | Path) -> CompletedProcess:
    """Mount a device."""

    return run(["/usr/bin/mount", str(device), str(mountpoint)], check=True, text=True)


def umount(mountpoint_or_device: str | Path) -> CompletedProcess:
    """Umount a mountpoint."""

    return run(["/usr/bin/umount", str(mountpoint_or_device)], check=True, text=True)
