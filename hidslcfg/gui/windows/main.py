"""Login window logic."""

from logging import getLogger
from subprocess import CalledProcessError
from threading import Thread

from hidslcfg.api import Client
from hidslcfg.common import HIDSL_DEBUG
from hidslcfg.gui.builder_window import BuilderWindow
from hidslcfg.gui.gtk import Gtk
from hidslcfg.gui.windows.login_tab import LoginTab
from hidslcfg.gui.windows.wifi_tab import WifiTab
from hidslcfg.system import ping, reboot


__all__ = ['MainWindow']


DEFAULT_HOST = 'wireguard.homeinfo.de'
LOGGER = getLogger(__file__)


class MainWindow(BuilderWindow, file='main.glade'):
    """Login form objects."""

    def __init__(self, client: Client):
        """Create the login form."""
        super().__init__('main', primary=self.build('tab_system_config'))
        self.client = client
        self.logged_in = False
        self.ping_successful: bool | None = None
        self.reboot_response = None

        # Login tab
        self.login_tab = LoginTab(self)

        # Wi-Fi tab
        self.wifi_tab = WifiTab(self)

        # Ping tab
        self.ping_hostname: Gtk.ComboBoxText = self.build('ping_hostname')
        self.ping_hostname.connect("changed", self.on_ping_hostname_change)
        self.ping_spinner: Gtk.Spinner = self.build('ping_spinner')
        self.ping_host: Gtk.Button = self.build('ping_host')
        self.ping_host_label: str = self.ping_host.get_label()
        self.ping_host.connect('activate', self.on_ping_host)
        self.ping_host.connect('clicked', self.on_ping_host)
        self.ping_result: Gtk.Image = self.build('ping_result')
        self.new_signal('ping-host-completed', self.on_ping_completed)

        self.btn_quit: Gtk.Button = self.build('quit')
        self.btn_quit.connect('activate', self.on_quit)
        self.btn_quit.connect('clicked', self.on_quit)

    def ping_thread(self) -> None:
        """Ping the host."""
        try:
            ping(self.ping_hostname.get_active_id())
        except CalledProcessError:
            self.ping_successful = False
        else:
            self.ping_successful = True

        self.window.emit('ping-host-completed', None)

    def on_ping_hostname_change(self, *_) -> None:
        """Ping the set host."""
        self.ping_result.set_from_icon_name(
            'face-plain-symbolic',
            Gtk.IconSize.LARGE_TOOLBAR
        )

    def on_ping_host(self, *args) -> None:
        """Ping the set host."""
        self.ping_host.set_property('sensitive', False)
        self.ping_hostname.set_property('sensitive', False)
        self.on_ping_hostname_change(*args)
        self.ping_host.set_label('')
        self.ping_spinner.start()
        Thread(daemon=True, target=self.ping_thread).start()

    def on_ping_completed(self, *_) -> None:
        """Sets the ping result."""
        self.ping_spinner.stop()
        self.ping_host.set_label(self.ping_host_label)
        self.ping_hostname.set_property('sensitive', True)
        self.ping_host.set_property('sensitive', True)

        if self.ping_successful:
            self.ping_result.set_from_icon_name(
                'face-smirk-symbolic',
                Gtk.IconSize.LARGE_TOOLBAR
            )
        else:
            self.ping_result.set_from_icon_name(
                'face-sad-symbolic',
                Gtk.IconSize.LARGE_TOOLBAR
            )

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
