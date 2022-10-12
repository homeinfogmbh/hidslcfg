"""Login window logic."""

from logging import getLogger
from subprocess import CalledProcessError
from threading import Thread

from hidslcfg.api import Client
from hidslcfg.common import HIDSL_DEBUG
from hidslcfg.exceptions import APIError
from hidslcfg.gui.builder_window import BuilderWindow
from hidslcfg.gui.gtk import Gtk
from hidslcfg.system import ping, reboot
from hidslcfg.wifi import MAX_PSK_LEN
from hidslcfg.wifi import MIN_PSK_LEN
from hidslcfg.wifi import configure
from hidslcfg.wifi import disable
from hidslcfg.wifi import from_magic_usb_key
from hidslcfg.wifi import load_wifi_configs
from hidslcfg.wifi import list_wifi_interfaces


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
        self.wifi_configs = load_wifi_configs()

        # Login tab
        self.user_name: Gtk.Entry = self.build('user_name')
        self.user_name.connect('activate', self.on_login)
        self.password: Gtk.Entry = self.build('password')
        self.password.connect('activate', self.on_login)
        self.login: Gtk.Button = self.build('login')
        self.login.connect('activate', self.on_login)
        self.login.connect('clicked', self.on_login)

        # Wi-Fi tab
        self.interfaces: Gtk.ComboBoxText = self.build('interfaces')
        self.load_wifi_config: Gtk.LinkButton = self.build('load_wifi_config')
        self.load_wifi_config.connect(
            'activate-link',
            self.on_load_wifi_config
        )
        self.interfaces.connect("changed", self.on_interface_select)
        self.ssid: Gtk.Entry = self.build('ssid')
        self.psk: Gtk.Entry = self.build('psk')
        self.configure_wifi: Gtk.Button = self.build('configure_wifi')
        self.configure_wifi.connect('activate', self.on_configure_wifi)
        self.configure_wifi.connect('clicked', self.on_configure_wifi)
        self.populate_interfaces()

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

    def populate_interfaces(self) -> None:
        """Populate interfaces combo box."""
        for index, interface in enumerate(list_wifi_interfaces()):
            self.interfaces.append_text(interface)

        self.interfaces.set_active(0)
        self.on_interface_select()

    def ping_thread(self) -> None:
        """Ping the host."""
        try:
            ping(self.ping_hostname.get_active_id())
        except CalledProcessError:
            self.ping_successful = False
        else:
            self.ping_successful = True

        self.window.emit('ping-host-completed', None)

    def on_login(self, *_) -> None:
        """Perform the login."""
        if not (user_name := self.user_name.get_text()):
            return self.show_error('Kein Benutzername angegeben.')

        if not (password := self.password.get_text()):
            return self.show_error('Kein Passwort angegeben.')

        try:
            self.client.login(user_name, password)
        except APIError as error:
            return self.show_error(error.json.get('message'))

        self.next_window()

    def on_interface_select(self, *_) -> None:
        """Set configuration for selected interface."""
        config = self.wifi_configs.get(self.interfaces.get_active_text(), {})
        self.ssid.set_text(config.get('ssid', ''))
        self.psk.set_text(config.get('psk', ''))

    def on_load_wifi_config(self, *_) -> None:
        """Attempt to load Wi-Fi config from USB."""
        try:
            config = from_magic_usb_key()
        except CalledProcessError:
            return self.show_error('Konnte USB-Stick nicht einhängen.')
        except FileNotFoundError:
            return self.show_error('Keine WLAN Konfigurationsdatei gefunden.')
        except PermissionError:
            return self.show_error(
                'Keine Berechtigung WLAN Konfigurationsdatei zu lesen.'
            )

        self.ssid.set_text(config.get('ssid', ''))
        self.psk.set_text(config.get('psk', ''))

    def on_configure_wifi(self, *_) -> None:
        """Configure the selected Wi-Fi interface."""
        if not (interface := self.interfaces.get_active_text()):
            return self.show_error('Keine WLAN Karte ausgewählt.')

        if not (ssid := self.ssid.get_text()):
            return self.show_error('Kein Netzwerkname angegeben.')

        if not (psk := self.psk.get_text()):
            return self.show_error('Kein Schlüssel angegeben.')

        if (psk_len := len(psk)) < MIN_PSK_LEN:
            return self.show_error(
                f'Schlüssel muss mindestens {MIN_PSK_LEN} Zeichen lang sein.'
            )

        if psk_len > MAX_PSK_LEN:
            return self.show_error(
                f'Schlüssel darf maximal {MAX_PSK_LEN} Zeichen lang sein.'
            )

        try:
            configure(interface, ssid, psk)
        except (CalledProcessError, PermissionError):
            return self.show_error('Konnte WLAN Verbindung nicht einrichten.')

        disable(set(list_wifi_interfaces()) - {interface})

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
