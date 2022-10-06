"""Completed window logic."""

from logging import getLogger

from hidslcfg.common import HIDSL_DEBUG
from hidslcfg.gui.builder_window import BuilderWindow
from hidslcfg.gui.gtk import Gtk
from hidslcfg.gui.setup_parameters import SetupParameters
from hidslcfg.system import reboot


__all__ = ['CompletedForm']


LOGGER = getLogger(__file__)


class CompletedForm(BuilderWindow, file='completed.glade'):
    """Installing form objects."""

    def __init__(self, setup_parameters: SetupParameters):
        """Create the installing form."""
        super().__init__(
            'completed',
            primary=(reboot_btn := self.build('reboot'))
        )
        self.setup_parameters = setup_parameters
        self.system_id: Gtk.Label = self.build('system_id')
        self.model: Gtk.Label = self.build('model')
        self.serial_number: Gtk.Label = self.build('serial_number')
        self.reboot: Gtk.Button = reboot_btn
        self.reboot.connect('activate', on_reboot)
        self.home: Gtk.Button = self.build('home')
        self.home.connect('activate', self.go_home)

    def on_show(self, *_) -> None:
        """Perform the setup process when window is shown."""
        self.system_id.set_text(f'{self.setup_parameters.system_id or "-"}')
        self.model.set_text(self.setup_parameters.model or '-')
        self.serial_number.set_text(
            f'{self.setup_parameters.serial_number or "-"}'
        )


def on_reboot(*_) -> None:
    """Reboot the system."""

    if HIDSL_DEBUG:
        LOGGER.warning('Not rebooting due to debug mode.')
        return Gtk.main_quit()

    reboot()
