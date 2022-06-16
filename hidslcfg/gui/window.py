"""Main window definitions."""

from hidslcfg.gui.gtk4 import Gtk


__all__ = ['MainWindow']


class MainWindow(Gtk.ApplicationWindow):
    """A GTK based GUI for RCON."""

    def __init__(self, title: str, width: int, height: int, **kwargs):
        """Initializes the GUI."""
        super().__init__(**kwargs)

        self.set_default_size(width, height)
        self.header_bar = Gtk.HeaderBar()
        self.set_titlebar(self.header_bar)
        self.header_bar.set_title_widget(make_label(title))
        # custom CSS provider
        self.css_provider = None


def make_label(text: str) -> Gtk.Label:
    """Create a label."""

    label = Gtk.Label()
    label.set_text(text)
    return label
