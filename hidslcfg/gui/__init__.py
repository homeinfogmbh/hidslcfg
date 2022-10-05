"""GTK based GUI."""

from os import getenv, geteuid
from sys import stderr

from hidslcfg.gui.gtk import Gtk
from hidslcfg.gui.main import MainBuilderWindow


def run() -> None:
    """Starts the GUI."""

    if not getenv('HIDSL_DEBUG') and geteuid() != 0:
        print('This program requires root privileges.', file=stderr)
        raise SystemExit(1)

    main_window = MainBuilderWindow()
    main_window.show()
    Gtk.main()


if __name__ == '__main__':
    run()
