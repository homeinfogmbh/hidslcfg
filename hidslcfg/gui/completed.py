"""Completed window logic."""

from __future__ import annotations

from hidslcfg.gui.functions import get_asset
from hidslcfg.gui.gtk import Gtk
from hidslcfg.gui.mixins import WindowMixin
from hidslcfg.system import reboot


__all__ = ['CompletedForm']


class CompletedForm(WindowMixin):
    """Installing form objects."""

    def __init__(
            self,
            system_id: int | None,
            serial_number: str | None,
            model: str
    ):
        """Create the installing form."""
        builder = Gtk.Builder()
        builder.add_from_file(str(get_asset('completed.glade')))
        self.window = builder.get_object('completed')
        self.system_id_label = builder.get_object('system_id')
        self.model_label = builder.get_object('model')
        self.serial_number_label = builder.get_object('serial_number')
        self.reboot_button = builder.get_object('reboot')
        builder.connect_signals(self.window)
        self.window.connect('destroy', Gtk.main_quit)
        self.reboot_button.connect('button-release-event', on_reboot)
        self.system_id_label.set_text(f'{system_id or "-"}')
        self.model_label.set_text(model)
        self.serial_number_label.set_text(f'{serial_number or "-"}')


def on_reboot(*_) -> None:
    """Reboot the system."""
    reboot()
