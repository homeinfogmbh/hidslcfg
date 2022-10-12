"""Window tabs."""

from __future__ import annotations

from hidslcfg.gui.builder_window import BuilderWindow


__all__ = ['SubElement']


class SubElement:
    """Window sub-element."""

    def __init__(self, window: BuilderWindow):
        self.builder_window: BuilderWindow = window

    def __getattr__(self, item):
        return getattr(self.builder_window, item)
