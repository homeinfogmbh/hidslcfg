"""Common mixins."""

from hidslcfg.gui.gtk import Gtk
from hidslcfg.gui.translation import translate


__all__ = ['WindowMixin']


class WindowMixin:
    """A window mixin."""

    def show(self) -> None:
        """Shows the window."""
        self.window.show()

    def show_error(self, message: str) -> None:
        """Shows an error message."""
        message_dialog = Gtk.MessageDialog(
            transient_for=self.window,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text=translate(message)
        )
        message_dialog.run()
        message_dialog.destroy()
