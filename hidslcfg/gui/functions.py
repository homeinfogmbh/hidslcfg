"""Main window definitions."""

from pathlib import Path

from hidslcfg.gui.gtk import Gtk


__all__ = ['get_xml', 'make_window']


def get_xml(filename: str) -> Path:
    """Returns the path to an XML GUI file."""

    return Path(__file__).parent / 'xml' / filename


def make_window(name: str, filename: Path) -> Gtk.ApplicationWindow:
    """Create a window."""

    builder = Gtk.Builder()
    builder.add_from_file(str(filename))
    window = builder.get_object(name)
    builder.connect_signals(window)
    print(window)
    return window
