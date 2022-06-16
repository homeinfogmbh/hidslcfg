"""Main GUI application."""

from hidslcfg.gui.gtk import Gtk
from hidslcfg.gui.functions import get_xml, make_window


def main() -> None:
    """Starts the GUI."""

    win = make_window('login', get_xml('login.glade'))
    win.show_all()
    Gtk.main()


if __name__ == '__main__':
    main()
