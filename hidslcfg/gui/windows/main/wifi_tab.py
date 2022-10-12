"""Login window logic."""

from subprocess import CalledProcessError
from threading import Thread

from hidslcfg.gui.builder_window import BuilderWindow
from hidslcfg.gui.sub_element import SubElement
from hidslcfg.gui.gtk import Gtk
from hidslcfg.wifi import MAX_PSK_LEN
from hidslcfg.wifi import MIN_PSK_LEN
from hidslcfg.wifi import configure
from hidslcfg.wifi import disable
from hidslcfg.wifi import from_magic_usb_key
from hidslcfg.wifi import load_wifi_configs
from hidslcfg.wifi import list_wifi_interfaces


__all__ = ['WifiTab']


class WifiTab(SubElement):
    """Wi-Fi setup tab."""

    def __init__(self, window: BuilderWindow):
        super().__init__(window)
        self.wifi_configs = load_wifi_configs()
        self.error_message: str | None = None
        self.interfaces: Gtk.ComboBoxText = self.build('interfaces')
        self.load_wifi_config: Gtk.LinkButton = self.build('load_wifi_config')
        self.ssid: Gtk.Entry = self.build('ssid')
        self.psk: Gtk.Entry = self.build('psk')
        self.configure_wifi: Gtk.Button = self.build('configure_wifi')
        self.wifi_interface = (
            self.interfaces,
            self.load_wifi_config,
            self.ssid,
            self.psk,
            self.configure_wifi
        )
        self.populate_interfaces()
        self.new_signal('load-wifi-config-done', self.on_load_wifi_config_done)
        self.new_signal('configure-wifi-done', self.wifi_gui_unlock)
        self.load_wifi_config.connect(
            'activate-link',
            self.on_load_wifi_config
        )
        self.interfaces.connect("changed", self.on_interface_select)
        self.configure_wifi.connect('activate', self.on_configure_wifi)
        self.configure_wifi.connect('clicked', self.on_configure_wifi)

    def on_load_wifi_config(self, *_) -> None:
        """After Wi-Fi config processing."""
        self.wifi_gui_lock()
        Thread(daemon=True, target=self.load_wifi_config_thread).start()

    def load_wifi_config_thread(self) -> None:
        """Perform actual Wi-Fi config loading."""
        error = None

        try:
            config = from_magic_usb_key()
        except CalledProcessError:
            error = 'Konnte USB-Stick nicht einhängen.'
        except FileNotFoundError:
            error = 'Keine WLAN Konfigurationsdatei gefunden.'
        except PermissionError:
            error = 'Keine Berechtigung WLAN Konfigurationsdatei zu lesen.'
        else:
            self.ssid.set_text(config.get('ssid', ''))
            self.psk.set_text(config.get('psk', ''))

        self.window.emit('load-wifi-config-done', error)

    def on_load_wifi_config_done(self, *args) -> None:
        """After Wi-Fi config processing."""
        self.wifi_gui_unlock()
        print(*args)

    def on_configure_wifi(self, *_) -> None:
        """Perform Wi-Fi configuration."""
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

        self.wifi_gui_lock()
        Thread(
            daemon=True,
            target=self.configure_wifi_thread,
            args=(interface, ssid, psk)
        ).start()

    def configure_wifi_thread(
            self, interface: str,
            ssid: str,
            psk: str
    ) -> None:
        """Thread to configure Wi-Fi."""
        try:
            configure(interface, ssid, psk)
        except (CalledProcessError, PermissionError):
            self.window.emit(
                'configure-wifi-done',
                'Konnte WLAN Verbindung nicht einrichten.'
            )
        else:
            disable(set(list_wifi_interfaces()) - {interface})
            self.window.emit('configure-wifi-done', None)

    def wifi_gui_lock(self) -> None:
        """Lock the Wi-Fi GUI."""
        for widget in self.wifi_interface:
            widget.set_property('sensitive', False)

    def wifi_gui_unlock(self, *_) -> None:
        """Unlock the Wi-Fi GUI."""
        for widget in self.wifi_interface:
            widget.set_property('sensitive', True)

    def on_interface_select(self, *_) -> None:
        """Set configuration for selected interface."""
        config = self.wifi_configs.get(self.interfaces.get_active_text(), {})
        self.ssid.set_text(config.get('ssid', ''))
        self.psk.set_text(config.get('psk', ''))

    def populate_interfaces(self) -> None:
        """Populate interfaces combo box."""
        for interface in list_wifi_interfaces():
            self.interfaces.append_text(interface)

        self.interfaces.set_active(0)
        self.on_interface_select()
