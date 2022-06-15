"""Main GUI application."""

from argparse import Namespace
from functools import partial
from logging import DEBUG, INFO, basicConfig, getLogger

from hidslcfg.common import LOG_FORMAT
from hidslcfg.gui.args import get_args
from hidslcfg.gui.gtk4 import Gtk


LOGGER = getLogger(NAME := 'HIDSL Installer')


class GUI(Gtk.ApplicationWindow):
    """A GTK based GUI for RCON."""

    def __init__(self, args: Namespace, **kwargs):
        """Initializes the GUI."""
        super().__init__(**kwargs)
        self.args = args


def init(args: Namespace, application: Gtk.Application) -> None:
    """Initializes the GUI."""

    win = GUI(args, application=application, title=NAME)
    win.fullscreen()
    win.present()


def main() -> None:
    """Starts the GUI."""

    args = get_args()
    basicConfig(format=LOG_FORMAT, level=DEBUG if args.debug else INFO)
    app = Gtk.Application(application_id='de.homeinfo.hidsl.installer')
    app.connect('activate', partial(init, args))
    app.run(None)


if __name__ == '__main__':
    main()
