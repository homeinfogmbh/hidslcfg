"""Common mixins."""

from __future__ import annotations
from typing import Any

from hidslcfg.gui.functions import get_asset
from hidslcfg.gui.gtk import EventHandler, Gtk, GObject
from hidslcfg.gui.translation import translate


__all__ = ['BuilderWindow']


class BuilderWindow:
    """A window mixin."""

    def __init__(self, name: str):
        """Initialize builder and main window."""
        self.next_window: Gtk.Window | None = None
        self.home_window: Gtk.Window | None = None
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
            action: EventHandler,
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
        self.next_window = next
        self.home_window = home
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

    def switch_window(self, window: Gtk.Window) -> None:
        """Switch to the given window."""
        self.window.hide()
        window.show()

    def go_home(self, *_) -> None:
        """Switch to the HOME window."""
        self.switch_window(self.home_window)

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
            text=translate(message)
        )
        message_dialog.run()
        message_dialog.destroy()

    def show_error(self, message: str) -> None:
        """Shows an error message."""
        self.show_message(message, message_type=Gtk.MessageType.ERROR)
