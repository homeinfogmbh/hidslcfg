"""Main GUI application."""

from os import geteuid
from sys import stderr

from hidslcfg.gui.gtk import Gtk
from hidslcfg.gui.login import LoginForm


def main() -> None:
    """Starts the GUI."""

    if geteuid() != 0:
        print('This program required root privileges.', file=stderr)
        raise SystemExit(1)

    login_form = LoginForm()
    login_form.show()
    Gtk.main()


if __name__ == '__main__':
    main()
