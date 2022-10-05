"""Common mixins."""

from typing import Any

from hidslcfg.gui.functions import get_asset
from hidslcfg.gui.gtk import Gtk
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
