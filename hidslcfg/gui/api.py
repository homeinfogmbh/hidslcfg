"""Common mixins."""

from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from gi import require_version
require_version('Gtk', '3.0')
require_version('Gdk', '3.0')
from gi.repository import Gdk, GLib, Gtk, GObject

from hidslcfg.common import HIDSL_DEBUG


__all__ = [
    'Gdk',
    'GLib',
    'Gtk',
    'GObject',
    'SetupParameters',
    'BuilderWindow',
    'SubElement'
]


ASSETS_DIR = Path('/usr/share/hidslcfg')
TRANSLATIONS = {
    'Invalid credentials.': 'Ungültige Anmeldedaten.'
}


@dataclass
class SetupParameters:
    """Setup parameters."""

    model: str | None = None
    system_id: int | None = None
    serial_number: str | None = None


class BuilderWindow:
    """A window mixin."""

    def __init__(self, name: str, *, primary: Gtk.Widget | None = None):
        """Initialize builder and main window."""
        self._next_window: BuilderWindow | None = None
        self._home_window: BuilderWindow | None = None
        self._primary_widget: Gtk.Widget | None = primary
        self.window: Gtk.Window = self.build(name)
        self.builder.connect_signals(self.window)
        self.window.connect('show', self.on_show)
        self.window.connect('destroy', self.on_destroy)

    def __init_subclass__(cls, file: str, **kwargs):
        """Set builder file and window name."""
        cls.builder = builder = Gtk.Builder()
        builder.add_from_file(str(get_asset(file)))

    def new_signal(
            self,
            name: str,
            action: Callable[[Gtk.Widget, Gdk.Event | Gdk.EventKey], None],
            *,
            signal: int = GObject.SIGNAL_RUN_LAST
    ) -> None:
        """Register a new signal."""
        GObject.signal_new(
            name, self.window,
            signal,
            GObject.TYPE_PYOBJECT,
            [GObject.TYPE_PYOBJECT]
        )
        self.window.connect(name, action)

    def bind(
            self,
            *,
            next: BuilderWindow | None = None,
            home: BuilderWindow | None = None
    ) -> BuilderWindow:
        """Bind the next an optionally the home window and
        returns the former allowing for a builder pattern.
        """
        self._next_window = next
        self._home_window = home
        return next

    def on_show(self, window: Gtk.ApplicationWindow) -> None:
        """Handle show event."""
        pass

    @staticmethod
    def on_destroy(_: Gtk.ApplicationWindow) -> None:
        """Handle destruction event."""
        return Gtk.main_quit()

    def build(self, name: str) -> Any:
        """Build the requested object."""
        return self.builder.get_object(name)

    def show(self) -> None:
        """Shows the window."""
        self.window.show()

        if self._primary_widget is not None:
            self.window.set_focus(self._primary_widget)

    def switch_window(self, window: BuilderWindow) -> None:
        """Switch to the given window."""
        self.window.hide()
        window.show()

    def go_home(self, *_) -> None:
        """Switch to the HOME window."""
        self.switch_window(self._home_window)

    def next_window(self) -> None:
        """Go to the next window."""
        self.switch_window(self._next_window)

    def show_message(
            self,
            message: str,
            message_type: Gtk.MessageType = Gtk.MessageType.INFO
    ) -> None:
        """Shows an error message."""
        message_dialog = Gtk.MessageDialog(
            transient_for=self.window,
            message_type=message_type,
            buttons=Gtk.ButtonsType.OK,
            text=TRANSLATIONS.get(message, message or 'NO_TEXT')
        )
        message_dialog.run()
        message_dialog.destroy()

    def show_error(self, message: str) -> None:
        """Shows an error message."""
        self.show_message(message, message_type=Gtk.MessageType.ERROR)


class SubElement:
    """Window sub-element."""

    def __init__(self, window: BuilderWindow):
        self.builder_window: BuilderWindow = window

    def __getattr__(self, item):
        return getattr(self.builder_window, item)


def get_asset(filename: str) -> Path:
    """Return the path to an asset file."""

    return get_base_dir() / filename


def get_base_dir() -> Path:
    """Return the assets base directory."""

    if HIDSL_DEBUG:
        return Path(__file__).parent / 'assets'

    return ASSETS_DIR
