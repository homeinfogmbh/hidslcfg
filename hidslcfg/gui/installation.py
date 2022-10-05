"""Installing window logic."""

from logging import getLogger
from os import getenv
from threading import Thread
from time import sleep

from hidslcfg.api import Client
from hidslcfg.exceptions import APIError, ProgramError
from hidslcfg.gui.builder_window import BuilderWindow
from hidslcfg.gui.completed import CompletedForm
from hidslcfg.gui.gtk import Gtk
from hidslcfg.wireguard import MTU, create, patch


__all__ = ['InstallationForm']


LOGGER = getLogger(__file__)
SLEEP = 3


class InstallationForm(BuilderWindow, file='installation.glade'):
    """installation form objects."""

    def __init__(
            self,
            client: Client,
            system_id: int | None,
            serial_number: str | None,
            model: str
    ):
        """Create the installation form."""
        super().__init__('installation')
        self.client = client
        self.system_id = system_id
        self.serial_number = serial_number
        self.model = model
        self.installed = False

    def on_show(self, *_) -> None:
        """Perform the setup process when window is shown."""
        Thread(daemon=True, target=self.safe_install).start()

    def on_destroy(self, *_) -> None:
        """Handle window destruction events."""
        if not self.installed:
            return Gtk.main_quit()

        completed_form = CompletedForm(
            self.system_id,
            self.serial_number,
            self.model
        )
        completed_form.show()

    def safe_install(self) -> None:
        """Run the installation with caught exceptions."""
        try:
            self.install()
        except ProgramError as error:
            self.show_error(str(error))
        except APIError as error:
            self.show_error(error.json.get('message'))
        except Exception as error:
            self.show_error(str(error))
        else:
            self.installed = True

        self.window.destroy()

    def install(self) -> None:
        """Run the installation."""
        if getenv('HIDSL_DEBUG'):
            LOGGER.warning('Sleeping for %s seconds due to debug mode.', SLEEP)
            return sleep(SLEEP)

        self.system_id = setup(
            self.client,
            self.system_id,
            self.serial_number,
            self.model
        )


def setup(
        client: Client,
        system_id: int | None,
        serial_number: str | None,
        model: str
) -> int:
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
