"""Login window logic."""

from logging import getLogger

from hidslcfg.api import Client
from hidslcfg.common import HIDSL_DEBUG
from hidslcfg.gui.api import Gtk, BuilderWindow
from hidslcfg.gui.windows.main.login_tab import LoginTab
from hidslcfg.gui.windows.main.ping_tab import PingTab
from hidslcfg.gui.windows.main.wifi_tab import WifiTab
from hidslcfg.system import reboot


__all__ = ['MainWindow']


LOGGER = getLogger(__file__)


class MainWindow(BuilderWindow, file='main.glade'):
    """Login form objects."""

    def __init__(self, client: Client):
        """Create the login form."""
        super().__init__('main', primary=self.build('tab_system_config'))
        self.client = client

        # Login tab
        self.login_tab = LoginTab(self)

        # Wi-Fi tab
        self.wifi_tab = WifiTab(self)

        # Ping tab
        self.ping_tab = PingTab(self)

        self.btn_quit: Gtk.Button = self.build('quit')
        self.btn_quit.connect('activate', self.on_quit)
        self.btn_quit.connect('clicked', self.on_quit)

    def on_quit(self, *_) -> None:
        """Handles the quit button."""
        message_dialog = Gtk.MessageDialog(
            transient_for=self.window,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text='Wollen Sie das System neu starten?'
        )
        response = message_dialog.run()
        message_dialog.destroy()

        if response == Gtk.ResponseType.YES:
            if not HIDSL_DEBUG:
                reboot()

            LOGGER.warning('Not rebooting due to debug mode.')

        Gtk.main_quit()
