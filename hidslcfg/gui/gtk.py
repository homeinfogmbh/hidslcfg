"""GTK 4 wrapper"""

from typing import Callable

from gi import require_version
require_version('Gtk', '3.0')
require_version('Gdk', '3.0')
from gi.repository import Gdk, Gtk


__all__ = ['Gtk', 'bind_keys']


def bind_keys(*widgets: Gtk.Widget, mapping: dict[str, Callable]) -> None:
    """Bind the pressing of keys to the respective widgets."""

    def on_key_press(_: Gtk.Widget, event: Gdk.EventKey) -> None:
        """Run an action based on the pressed key."""
        if function := mapping.get(event.keyval):
            function()

    for widget in widgets:
        widget.connect('key-press-event', on_key_press)
