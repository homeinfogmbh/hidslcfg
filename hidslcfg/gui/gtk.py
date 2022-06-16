"""GTK 4 wrapper"""

from gi import require_version
require_version('Gtk', '3.0')
from gi.repository import Gio, Gtk


__all__ = ['Gio', 'Gtk']
