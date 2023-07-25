"""Login window logic."""

from subprocess import CalledProcessError
from threading import Thread

from hidslcfg.gui.api import GLib, Gtk, BuilderWindow, SubElement
from hidslcfg.wifi import MAX_PSK_LEN
from hidslcfg.wifi import MIN_PSK_LEN
from hidslcfg.wifi import configure
from hidslcfg.wifi import disable
from hidslcfg.wifi import from_magic_usb_key
from hidslcfg.wifi import load_wifi_configs
from hidslcfg.wifi import list_wifi_interfaces


__all__ = ["WifiTab"]


class WifiTab(SubElement):
    """Wi-Fi setup tab."""

    def __init__(self, window: BuilderWindow):
        super().__init__(window)
        self.wifi_configs = load_wifi_configs()
        self.interfaces: Gtk.ComboBoxText = self.build("interfaces")
        self.load_config: Gtk.LinkButton = self.build("load_wifi_config")
        self.ssid: Gtk.Entry = self.build("ssid")
        self.psk: Gtk.Entry = self.build("psk")
        self.configure: Gtk.Button = self.build("configure_wifi")
        self.populate_interfaces()
        self.load_config.connect("activate-link", self.on_load_config)
        self.interfaces.connect("changed", self.on_interface_select)
        self.configure.connect("activate", self.on_configure)
        self.configure.connect("clicked", self.on_configure)

    def populate_interfaces(self) -> None:
        """Populate interfaces combo box."""
        for interface in list_wifi_interfaces():
            self.interfaces.append_text(interface)

        self.interfaces.set_active(0)
        self.on_interface_select()

    def on_interface_select(self, *_) -> None:
        """Set configuration for selected interface."""
        config = self.wifi_configs.get(self.interfaces.get_active_text(), {})
        self.ssid.set_text(config.get("ssid", ""))
        self.psk.set_text(config.get("psk", ""))

    def on_load_config(self, *_) -> None:
        """After Wi-Fi config processing."""
        self.lock_gui()
        Thread(daemon=True, target=self.load_config_thread).start()

    def load_config_thread(self) -> None:
        """Load the configuration from the magic USB key."""
        config = {}
        error = None

        try:
            config = from_magic_usb_key()
        except CalledProcessError:
            error = "Konnte USB-Stick nicht einhängen."
        except FileNotFoundError:
            error = "Keine WLAN Konfigurationsdatei gefunden."
        except PermissionError:
            error = "Keine Berechtigung WLAN Konfigurationsdatei zu lesen."

        GLib.idle_add(lambda: self.on_load_config_done(config, error))

    def on_load_config_done(self, config: dict, error: str | None) -> None:
        """Run when configuration is done."""
        self.ssid.set_text(config.get("ssid", ""))
        self.psk.set_text(config.get("psk", ""))
        self.unlock_gui()

        if error:
            self.show_error(error)

    def on_configure(self, *_) -> None:
        """Perform Wi-Fi configuration."""
        if not (interface := self.interfaces.get_active_text()):
            return self.show_error("Keine WLAN Karte ausgewählt.")

        if not (ssid := self.ssid.get_text()):
            return self.show_error("Kein Netzwerkname angegeben.")

        if not (psk := self.psk.get_text()):
            return self.show_error("Kein Schlüssel angegeben.")

        if (psk_len := len(psk)) < MIN_PSK_LEN:
            return self.show_error(
                f"Schlüssel muss mindestens {MIN_PSK_LEN} Zeichen lang sein."
            )

        if psk_len > MAX_PSK_LEN:
            return self.show_error(
                f"Schlüssel darf maximal {MAX_PSK_LEN} Zeichen lang sein."
            )

        self.lock_gui()
        Thread(
            daemon=True, target=self.configure_thread, args=(interface, ssid, psk)
        ).start()

    def configure_thread(self, interface: str, ssid: str, psk: str) -> None:
        """Actually perform the configuration."""
        error = None

        try:
            configure(interface, ssid, psk)
        except (CalledProcessError, PermissionError):
            error = "Konnte WLAN Verbindung nicht einrichten."
        else:
            disable(set(list_wifi_interfaces()) - {interface})

        GLib.idle_add(lambda: self.on_configure_done(error))

    def on_configure_done(self, error: str | None) -> None:
        """Callback when configuration is done."""
        self.unlock_gui()

        if error:
            return self.show_error(error)
