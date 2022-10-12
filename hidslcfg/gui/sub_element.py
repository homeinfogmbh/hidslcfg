"""Window tabs."""

from __future__ import annotations

from hidslcfg.gui.builder_window import BuilderWindow
from hidslcfg.gui.gtk import Gtk


__all__ = ['SubElement']


class SubElement:
    """Window sub-element."""

    def __init__(self, window: Gtk.Window, builder: Gtk.Builder):
        self.window: Gtk.Window = window
        self.builder: Gtk.Builder = builder

    @classmethod
    def from_window(cls, window: BuilderWindow) -> SubElement:
        """Create a sub-element from the main window."""
        return cls(window.window, window.builder)
