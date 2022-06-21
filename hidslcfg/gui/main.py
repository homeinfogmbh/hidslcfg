"""Main GUI application."""

from hidslcfg.gui.gtk import Gtk
from hidslcfg.gui.login import LoginForm


def main() -> None:
    """Starts the GUI."""

    login_form = LoginForm.create()
    login_form.login_button.connect('button-release-event', login_form.login)
    login_form.show()
    Gtk.main()


if __name__ == '__main__':
    main()
