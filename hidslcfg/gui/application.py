"""Main GTK application."""

from hidslcfg.gui.gtk4 import Gio, Gtk
from hidslcfg.gui.window import MainWindow


__all__ = ['Application']


class Application(Gtk.Application):
    """ Main Application class """

    def __init__(self):
        super().__init__(
            application_id='de.homeinfo.hidsl.cfg',
            flags=Gio.ApplicationFlags.FLAGS_NONE
        )

    def do_activate(self):
        if not (win := self.props.active_window):
            win = MainWindow('HIDSL Configurator', 800, 800, application=self)

        win.present()
