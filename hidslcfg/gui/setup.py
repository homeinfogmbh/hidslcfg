"""Setup window logic."""

from functools import partial
from os import geteuid

from hidslcfg.api import Client
from hidslcfg.gui.functions import get_asset
from hidslcfg.gui.installation import InstallationForm
from hidslcfg.gui.mixins import WindowMixin
from hidslcfg.gui.gtk import Gtk


__all__ = ['SetupForm']


class ModelOptions:
    """Model options."""

    def __init__(self, builder: Gtk.Builder):
        """Create model options from the given builder."""
        self.standard24 = builder.get_object('standard24')
        self.standard24.connect('toggled', self.on_select)
        self.standard32 = builder.get_object('standard32')
        self.standard32.connect('toggled', self.on_select)
        self.neptun = builder.get_object('neptun')
        self.neptun.connect('toggled', self.on_select)
        self.phoenix = builder.get_object('phoenix')
        self.phoenix.connect('toggled', self.on_select)
        self.concealed24 = builder.get_object('concealed24')
        self.concealed24.connect('toggled', self.on_select)
        self.concealed32 = builder.get_object('concealed32')
        self.concealed32.connect('toggled', self.on_select)
        self.other_model = builder.get_object('other_model')
        self.other_model.connect('toggled', partial(self.on_select, None))
        self.model = builder.get_object('model')
        self._selected = self.standard24.get_label()

    @property
    def selected(self) -> str:
        """Return the selected model name."""
        if self._selected is None:
            if text := self.model.get_text():
                return text

            raise ValueError('No model selected.')

        return self._selected

    def on_select(self, widget: Gtk.RadioButton | None, *_):
        """Handle select events."""
        self._selected = None if widget is None else widget.get_label()


class SetupForm(WindowMixin):
    """Setup form objects."""

    def __init__(self, client: Client):
        """Create the setup form."""
        self.client = client
        self._installing = False
        self._system_id = None
        self._serial_number = None
        self._model = None
        builder = Gtk.Builder()
        builder.add_from_file(str(get_asset('setup.glade')))
        self.window = builder.get_object('setup')
        self.serial_number = builder.get_object('serial_number')
        self.system_id = builder.get_object('system_id')
        self.install = builder.get_object('install')
        self.model_options = ModelOptions(builder)
        builder.connect_signals(self.window)
        self.window.connect('destroy', Gtk.main_quit)
        self.install.connect('button-release-event', self.on_setup)

    def get_system_id(self) -> int | None:
        """Return the system ID."""
        if system_id := self.system_id.get_text():
            return int(system_id)

        return None

    def on_destroy(self, *_) -> None:
        """Handle window destruction events."""
        if self._installing:
            installation_form = InstallationForm(
                self.client,
                self._system_id,
                self._serial_number,
                self._model
            )
            installation_form.show()
            installation_form.setup()
        else:
            Gtk.main_quit()

    def on_setup(self, *_) -> None:
        """Perform the installation."""
        if geteuid() != 0:
            return self.show_error(
                'Das Programm muss als Benutzer "root" ausgeführt werden.'
            )

        try:
            self._system_id = self.get_system_id()
        except ValueError:
            return self.show_error('Ungültige System ID.')

        try:
            self._model = self.model_options.selected
        except ValueError:
            return self.show_error('Kein Modell angegeben.')

        self._serial_number = self.serial_number.get_text() or None
        self._installing = True
        self.window.destroy()
