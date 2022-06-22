"""Installing window logic."""

from hidslcfg.api import Client
from hidslcfg.exceptions import APIError, ProgramError
from hidslcfg.gui.completed import CompletedForm
from hidslcfg.gui.functions import get_asset
from hidslcfg.gui.gtk import Gtk
from hidslcfg.gui.mixins import WindowMixin
from hidslcfg.wireguard import MTU, create, patch


__all__ = ['InstallationForm']


class InstallationForm(WindowMixin):
    """installation form objects."""

    def __init__(
            self,
            client: Client,
            system_id: int | None,
            serial_number: str | None,
            model: str
    ):
        """Create the installation form."""
        self.client = client
        self.system_id = system_id
        self.serial_number = serial_number
        self.model = model
        self.installed = False
        builder = Gtk.Builder()
        builder.add_from_file(str(get_asset('installation.glade')))
        self.window = builder.get_object('installation')
        builder.connect_signals(self.window)
        self.window.connect('destroy', self.on_destroy)

    def on_destroy(self, *args, **kwargs) -> None:
        """Handle window destruction events."""
        if not self.installed:
            return Gtk.main_quit(*args, **kwargs)

        completed_form = CompletedForm(
            self.system_id,
            self.serial_number,
            self.model
        )
        completed_form.show()

    def setup(self) -> None:
        """Perform the setup process."""
        try:
            setup(
                self.client,
                self.system_id,
                self.serial_number,
                self.model
            )
        except ProgramError as error:
            self.show_error(str(error))
        except APIError as error:
            self.show_error(error.json.get('message'))
        except Exception as error:
            self.show_error(str(error))
        else:
            self.installed = True

        self.window.destroy()


def setup(
        client: Client,
        system_id: int | None,
        serial_number: str | None,
        model: str
) -> None:
    """Run the setup."""

    if system_id is None:
        return create(
            client, mtu=MTU, os='Arch Linux', model=model, sn=serial_number,
            group=1
        )

    return patch(
        client, system_id, mtu=MTU, os='Arch Linux', model=model,
        sn=serial_number
    )
