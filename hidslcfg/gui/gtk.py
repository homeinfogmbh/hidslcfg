"""GTK 4 wrapper"""

from typing import Callable

from gi import require_version
require_version('Gtk', '3.0')
require_version('Gdk', '3.0')
from gi.repository import Gdk, Gtk


__all__ = ['Gtk', 'bind_button']


ENTER_KEY = 65293

EventHandler = Callable[[Gtk.Widget, Gdk.EventKey], None]


def bind_button(button: Gtk.Button, function: EventHandler) -> None:
    """Bind an event to a button activation."""

    def on_key_press(widget: Gtk.Widget, event: Gdk.EventKey) -> None:
        """Run an action based on the pressed key."""
        if event.keyval == ENTER_KEY:
            function(widget, event)

    button.connect('key-press-event', on_key_press)
    button.connect('button-release-event', function)
