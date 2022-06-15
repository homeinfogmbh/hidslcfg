"""GTK 4 wrapper"""

from gi import require_version
require_version('Gtk', '4.0')
from gi.repository import Gtk


__all__ = ['Gtk']
