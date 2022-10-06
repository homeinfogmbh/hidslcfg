"""Installing window logic."""

from logging import getLogger
from threading import Thread
from time import sleep

from hidslcfg.api import Client
from hidslcfg.common import HIDSL_DEBUG
from hidslcfg.exceptions import APIError, ProgramError
from hidslcfg.gui.builder_window import BuilderWindow
from hidslcfg.gui.setup_parameters import SetupParameters
from hidslcfg.wireguard import MTU, create, patch


__all__ = ['InstallationForm']


LOGGER = getLogger(__file__)
SLEEP = 3


class InstallationForm(BuilderWindow, file='installation.glade'):
    """installation form objects."""

    def __init__(self, client: Client, setup_parameters: SetupParameters):
        """Create the installation form."""
        super().__init__('installation')
        self.client = client
        self.setup_parameters: SetupParameters = setup_parameters
        self.new_signal('installation-completed', self.continue_to_next_window)

    def on_show(self, *_) -> None:
        """Perform the setup process when window is shown."""
        Thread(daemon=True, target=self.safe_install).start()

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

        self.window.emit('installation-completed', None)

    def install(self) -> None:
        """Run the installation."""
        if HIDSL_DEBUG:
            LOGGER.warning('Sleeping for %s seconds due to debug mode.', SLEEP)
            return sleep(SLEEP)

        self.setup_parameters.system_id = setup(
            self.client,
            self.setup_parameters.system_id,
            self.setup_parameters.serial_number,
            self.setup_parameters.model
        )

    def continue_to_next_window(self, *_) -> None:
        """Continue to the next window."""
        self.switch_window(self.next_window)


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
