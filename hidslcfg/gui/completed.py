"""Completed window logic."""

from logging import getLogger
from os import getenv

from hidslcfg.gui.builder_window import BuilderWindow
from hidslcfg.gui.gtk import Gtk, bind_button
from hidslcfg.gui.main import MainWindow
from hidslcfg.system import reboot


__all__ = ['CompletedForm']


LOGGER = getLogger(__file__)


class CompletedForm(BuilderWindow, file='completed.glade'):
    """Installing form objects."""

    def __init__(
            self,
            system_id: int | None,
            serial_number: str | None,
            model: str
    ):
        """Create the installing form."""
        super().__init__('completed')
        self.go_home = False

        self.system_id: Gtk.Label = self.build('system_id')
        self.system_id.set_text(f'{system_id or "-"}')
        self.model: Gtk.Label = self.build('model')
        self.model.set_text(model)
        self.serial_number: Gtk.Label = self.build('serial_number')
        self.serial_number.set_text(f'{serial_number or "-"}')
        self.reboot: Gtk.Button = self.build('reboot')
        bind_button(self.reboot, on_reboot)
        self.home: Gtk.Label = self.build('home')
        self.home.connect('button-release-event', self.on_go_home)

    def on_go_home(self, *_):
        """Set flag to return to home screen."""
        self.go_home = True

    def on_destroy(self, *args) -> None:
        """Handle window destruction events."""
        if self.go_home:
            main_window = MainWindow()
            main_window.show()
        else:
            Gtk.main_quit()


def on_reboot(*_) -> None:
    """Reboot the system."""

    if getenv('HIDSL_DEBUG'):
        LOGGER.warning('Not rebooting due to debug mode.')
        return Gtk.main_quit()

    reboot()
