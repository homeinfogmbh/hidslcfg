"""GTK 4 wrapper"""

from gi import require_version
require_version('Gtk', '3.0')
require_version('Gdk', '3.0')
from gi.repository import Gdk, Gtk, GObject


__all__ = ['Gdk', 'Gtk', 'GObject']
