"""Setup window logic."""

from enum import Enum, auto
from functools import partial
from typing import Any, Callable

from hidslcfg.api import Client
from hidslcfg.gui.builder_window import BuilderWindow
from hidslcfg.gui.gtk import Gtk, bind_action
from hidslcfg.gui.setup_parameters import SetupParameters


__all__ = ['SetupForm']


class CloseAction(Enum):
    """Close action to run."""

    SETUP = auto()
    GO_HOME = auto()


class SetupForm(BuilderWindow, file='setup.glade'):
    """Setup form objects."""

    def __init__(self, client: Client, parameters: SetupParameters):
        """Create the setup form."""
        super().__init__('setup')
        self.client = client
        self.parameters = parameters
        self.primary_widget: Gtk.Widget = self.build('standard24')

        self.serial_number: Gtk.Entry = self.build('serial_number')
        self.system_id: Gtk.Entry = self.build('system_id')
        self.model_options = ModelOptions(self.build)
        self.install: Gtk.Button = self.build('install')
        bind_action(self.on_setup, self.install)
        self.home: Gtk.Button = self.build('home')
        bind_action(self.go_home, self.home)

    def get_system_id(self) -> int | None:
        """Return the system ID."""
        if system_id := self.system_id.get_text():
            return int(system_id)

        return None

    def on_setup(self, *_) -> None:
        """Perform the installation."""
        try:
            self.parameters.system_id = self.get_system_id()
        except ValueError:
            return self.show_error('Ungültige System ID.')

        try:
            self.parameters.model = self.model_options.selected
        except ValueError:
            return self.show_error('Kein Modell angegeben.')

        self.parameters.serial_number = self.serial_number.get_text() or None
        self.switch_window(self.next_window)


class ModelOptions:
    """Model options."""

    def __init__(self, build: Callable[[str], Any]):
        """Create model options from the given builder."""
        self.standard24: Gtk.RadioButton = build('standard24')
        self.standard24.connect('toggled', self.on_select)
        self.standard32: Gtk.RadioButton = build('standard32')
        self.standard32.connect('toggled', self.on_select)
        self.neptun: Gtk.RadioButton = build('neptun')
        self.neptun.connect('toggled', self.on_select)
        self.phoenix: Gtk.RadioButton = build('phoenix')
        self.phoenix.connect('toggled', self.on_select)
        self.concealed24: Gtk.RadioButton = build('concealed24')
        self.concealed24.connect('toggled', self.on_select)
        self.concealed32: Gtk.RadioButton = build('concealed32')
        self.concealed32.connect('toggled', self.on_select)
        self.other_model: Gtk.RadioButton = build('other_model')
        self.other_model.connect('toggled', partial(self.on_select, None))
        self.model: Gtk.Entry = build('model')
        self._selected: Gtk.RadioButton = self.standard24

    @property
    def selected(self) -> str:
        """Return the selected model name."""
        if self._selected is None:
            if text := self.model.get_text():
                return text

            raise ValueError('No model selected.')

        return self._selected.get_label()

    def on_select(self, widget: Gtk.RadioButton | None, *_):
        """Handle select events."""
        self._selected = None if widget is None else widget
