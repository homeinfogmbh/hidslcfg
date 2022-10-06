"""GTK 4 wrapper"""

from typing import Callable

from gi import require_version
require_version('Gtk', '3.0')
require_version('Gdk', '3.0')
from gi.repository import Gdk, Gtk, GObject


__all__ = ['EventHandler', 'Gdk', 'Gtk', 'GObject', 'bind_action']


ENTER_KEY = 65293

EventHandler = Callable[[Gtk.Widget, Gdk.Event | Gdk.EventKey], None]


def bind_action(action: EventHandler, *widgets: Gtk.Widget) -> None:
    """Bind an event to a button activation."""

    def on_key_press(caller: Gtk.Widget, event: Gdk.EventKey) -> None:
        """Run an action based on the pressed key."""
        if event.keyval == ENTER_KEY:
            action(caller, event)

    for widget in widgets:
        widget.connect('key-release-event', on_key_press)

        if isinstance(widget, Gtk.Button):
            widget.connect('button-release-event', action)
