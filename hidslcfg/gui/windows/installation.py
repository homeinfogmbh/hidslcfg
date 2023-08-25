"""Installing window logic."""

from logging import getLogger
from threading import Thread
from time import sleep

from hidslcfg.api import Client
from hidslcfg.common import HIDSL_DEBUG
from hidslcfg.exceptions import APIError, ProgramError
from hidslcfg.gui.api import GLib, Gtk, BuilderWindow, SetupParameters
from hidslcfg.system import is_ddb_os_system
from hidslcfg.wireguard import MTU, create, patch


__all__ = ["InstallationForm"]


LOGGER = getLogger(__file__)
SLEEP = 3


class InstallationForm(BuilderWindow, file="installation.glade"):
    """installation form objects."""

    def __init__(self, client: Client, setup_parameters: SetupParameters):
        """Create the installation form."""
        super().__init__("installation")
        self.client = client
        self.setup_parameters: SetupParameters = setup_parameters
        self.spinner: Gtk.Spinner = self.build("spinner")

    def on_show(self, *_) -> None:
        """Perform the setup process when window is shown."""
        self.spinner.start()
        Thread(daemon=True, target=self.safe_install).start()

    def safe_install(self) -> None:
        """Run the installation with caught exceptions."""
        try:
            self.install()
        except ProgramError as program_error:
            error = str(program_error)
        except APIError as api_error:
            error = str(api_error)
        except Exception as exception:
            error = str(exception)
        else:
            error = None

        GLib.idle_add(lambda: self.on_installation_completed(error))

    def install(self) -> None:
        """Run the installation."""
        if HIDSL_DEBUG:
            LOGGER.warning("Sleeping for %s seconds due to debug mode.", SLEEP)
            return sleep(SLEEP)

        self.setup_parameters.system_id = setup(
            self.client,
            self.setup_parameters.system_id,
            self.setup_parameters.serial_number,
            self.setup_parameters.model,
        )

    def on_installation_completed(self, error: str | None) -> None:
        """Continue to the next window."""
        self.spinner.stop()

        if error:
            self.show_error(error)

        self.next_window()


def setup(
    client: Client, system_id: int | None, serial_number: str | None, model: str
) -> int:
    """Run the setup."""

    if system_id is None:
        return create(
            client,
            mtu=MTU,
            os="Arch Linux",
            model=model,
            sn=serial_number,
            group=1,
            ddb_os=is_ddb_os_system(),
        )

    return patch(
        client,
        system_id,
        mtu=MTU,
        os="Arch Linux",
        model=model,
        sn=serial_number,
        ddb_os=is_ddb_os_system(),
    )
