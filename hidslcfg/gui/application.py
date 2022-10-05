"""GUI application."""

from os import geteuid
from sys import stderr

from hidslcfg.api import Client
from hidslcfg.common import HIDSL_DEBUG
from hidslcfg.gui.completed import CompletedForm
from hidslcfg.gui.gtk import Gtk
from hidslcfg.gui.installation import InstallationForm
from hidslcfg.gui.main import MainWindow
from hidslcfg.gui.setup import SetupForm
from hidslcfg.gui.setup_parameters import SetupParameters


__all__ = ['run']


def run() -> None:
    """Run the GUI."""

    if not HIDSL_DEBUG and geteuid() != 0:
        print('This program requires root privileges.', file=stderr)
        raise SystemExit(1)

    client = Client()
    setup_parameters = SetupParameters()

    main_window = MainWindow(client)

    setup_form = SetupForm(client, setup_parameters)
    setup_form.home_window = main_window
    main_window.next_window = setup_form

    installation_form = InstallationForm(client, setup_parameters)
    installation_form.home_window = main_window
    setup_form.next_window = installation_form

    completed_form = CompletedForm(setup_parameters)
    completed_form.home_window = main_window
    installation_form.next_window = completed_form

    main_window.show()
    Gtk.main()


if __name__ == '__main__':
    run()
