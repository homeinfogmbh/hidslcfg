"""Login window logic."""

from subprocess import CalledProcessError
from threading import Thread

from hidslcfg.api import Client
from hidslcfg.exceptions import APIError
from hidslcfg.gui.builder_window import BuilderWindow
from hidslcfg.gui.gtk import Gtk, bind_action
from hidslcfg.system import ping
from hidslcfg.wifi import MAX_PSK_LEN
from hidslcfg.wifi import MIN_PSK_LEN
from hidslcfg.wifi import configure
from hidslcfg.wifi import disable
from hidslcfg.wifi import load_wifi_configs
from hidslcfg.wifi import list_wifi_interfaces


__all__ = ['MainWindow']


DEFAULT_HOST = 'wireguard.homeinfo.de'


class MainWindow(BuilderWindow, file='main.glade'):
    """Login form objects."""

    def __init__(self, client: Client):
        """Create the login form."""
        super().__init__('main')
        self.client = client
        self.logged_in = False
        self.ping_host_label: str | None = None
        self.ping_successful: bool | None = None
        self.wifi_configs = load_wifi_configs()

        # Tabs
        self.tabs: Gtk.Notebook = self.build('tabs')
        self.tabs.connect('switch-page', self.reset_tabs)

        # Login tab
        self.user_name: Gtk.Entry = self.build('user_name')
        self.password: Gtk.Entry = self.build('password')
        self.login: Gtk.Button = self.build('login')
        bind_action(self.on_login, self.user_name, self.password, self.login)

        # WIFI tab
        self.interfaces: Gtk.ComboBoxText = self.build('interfaces')
        self.populate_interfaces()
        self.interfaces.connect("changed", self.on_interface_select)
        self.ssid: Gtk.Entry = self.build('ssid')
        self.psk: Gtk.Entry = self.build('psk')
        self.configure_wifi: Gtk.Button = self.build('configure_wifi')
        bind_action(self.on_configure_wifi, self.configure_wifi)

        # Ping tab
        self.ping_hostname: Gtk.Entry = self.build('ping_hostname')
        self.ping_spinner: Gtk.Spinner = self.build('ping_spinner')
        self.ping_host: Gtk.Button = self.build('ping_host')
        self.ping_result: Gtk.Label = self.build('ping_result')
        bind_action(self.on_ping_host, self.ping_hostname, self.ping_host)
        self.new_signal('ping-host-completed', self.on_ping_completed)

    def populate_interfaces(self) -> None:
        """Populate interfaces combo box."""
        for index, interface in enumerate(list_wifi_interfaces()):
            self.interfaces.append_text(interface)

        self.interfaces.set_active(0)

    def reset_tabs(self, _: Gtk.Notebook, __: Gtk.Widget, index: int) -> None:
        """Reset the tabs' content."""
        if index == 2:
            self.ping_hostname.set_text(DEFAULT_HOST)

    def ping_thread(self) -> None:
        """Ping the host."""
        try:
            ping(self.ping_hostname.get_text())
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

        self.switch_window(self.next_window)

    def on_interface_select(self, *_):
        """Set configuration for selected interface."""
        config = self.wifi_configs.get(self.interfaces.get_active_text(), {})
        self.ssid.set_text(config.get('ssid', ''))
        self.psk.set_text(config.get('psk', ''))

    def on_configure_wifi(self, *_) -> None:
        """Configure the selected WIFI interface."""
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

    def on_ping_host(self, *_):
        """Ping the set host."""
        self.ping_hostname.set_text(self.ping_hostname.get_text().strip())
        self.ping_result.set_text('')
        self.ping_host_label = self.ping_host.get_label()
        self.ping_host.set_label('')
        self.ping_spinner.start()
        Thread(daemon=True, target=self.ping_thread).start()

    def on_ping_completed(self, *_) -> None:
        """Sets the ping result."""
        self.ping_spinner.stop()
        self.ping_host.set_label(self.ping_host_label)

        if self.ping_successful:
            self.ping_result.set_text('Verbindungstest erfolgreich.')
        else:
            self.ping_result.set_text('Verbindungstest fehlgeschlagen.')
