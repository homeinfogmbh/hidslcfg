"""Setup window logic."""

from enum import Enum, auto
from functools import partial
from typing import Callable

from hidslcfg.api import Client
from hidslcfg.gui.api import Gtk, GObjectT, BuilderWindow, SetupParameters


__all__ = ["SetupForm"]


class CloseAction(Enum):
    """Close action to run."""

    SETUP = auto()
    GO_HOME = auto()


class SetupForm(BuilderWindow, file="setup.glade"):
    """Setup form objects."""

    def __init__(self, client: Client, parameters: SetupParameters):
        """Create the setup form."""
        super().__init__("setup", primary=self.build("standard24"))
        self.client = client
        self.parameters = parameters

        self.serial_number: Gtk.Entry = self.build("serial_number")
        self.system_id: Gtk.Entry = self.build("system_id")
        self.model_options = ModelOptions(self.build)
        self.install: Gtk.Button = self.build("install")
        self.install.connect("activate", self.on_setup)
        self.install.connect("clicked", self.on_setup)
        self.home: Gtk.Button = self.build("home")
        self.home.connect("activate", self.go_home)
        self.home.connect("clicked", self.go_home)

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
            return self.show_error("Ungültige System ID.")

        try:
            self.parameters.model = self.model_options.selected
        except ValueError:
            return self.show_error("Kein Modell angegeben.")

        self.parameters.serial_number = self.serial_number.get_text() or None
        self.next_window()


class ModelOptions:
    """Model options."""

    def __init__(self, build: Callable[[str], GObjectT]):
        """Create model options from the given builder."""
        self.standard24: Gtk.RadioButton = build("standard24")
        self.standard24.connect("toggled", self.on_select)
        self.standard32: Gtk.RadioButton = build("standard32")
        self.standard32.connect("toggled", self.on_select)
        self.neptun: Gtk.RadioButton = build("neptun")
        self.neptun.connect("toggled", self.on_select)
        self.phoenix: Gtk.RadioButton = build("phoenix")
        self.phoenix.connect("toggled", self.on_select)
        self.concealed24: Gtk.RadioButton = build("concealed24")
        self.concealed24.connect("toggled", self.on_select)
        self.concealed32: Gtk.RadioButton = build("concealed32")
        self.concealed32.connect("toggled", self.on_select)
        self.other_model: Gtk.RadioButton = build("other_model")
        self.other_model.connect("toggled", partial(self.on_select, None))
        self.model: Gtk.Entry = build("model")
        self._selected: Gtk.RadioButton = self.standard24

    @property
    def selected(self) -> str:
        """Return the selected model name."""
        if self._selected is None:
            if text := self.model.get_text():
                return text

            raise ValueError("No model selected.")

        return self._selected.get_label()

    def on_select(self, widget: Gtk.RadioButton | None, *_):
        """Handle select events."""
        self._selected = None if widget is None else widget
