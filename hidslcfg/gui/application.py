"""GUI application."""

from os import geteuid
from sys import stderr

from hidslcfg.api import Client
from hidslcfg.common import HIDSL_DEBUG
from hidslcfg.gui.api import Gtk, SetupParameters
from hidslcfg.gui.windows import CompletedForm
from hidslcfg.gui.windows import InstallationForm
from hidslcfg.gui.windows import MainWindow
from hidslcfg.gui.windows import SetupForm


__all__ = ['run']


def run() -> None:
    """Run the GUI."""

    if not HIDSL_DEBUG and geteuid() != 0:
        print('This program requires root privileges.', file=stderr)
        raise SystemExit(1)

    client = Client()
    setup_parameters = SetupParameters()

    home_window = MainWindow(client)

    home_window.bind(
        next=SetupForm(client, setup_parameters)
    ).bind(
        next=InstallationForm(client, setup_parameters),
        home=home_window
    ).bind(
        next=CompletedForm(setup_parameters),
        home=home_window
    ).bind(
        next=None,
        home=home_window
    )

    home_window.show()
    Gtk.main()


if __name__ == '__main__':
    run()
