"""Login window logic."""

from subprocess import CalledProcessError
from threading import Thread

from hidslcfg.gui.api import GLib, Gtk, BuilderWindow, SubElement
from hidslcfg.system import ping


__all__ = ['PingTab']


class PingTab(SubElement):
    """Ping test tab."""

    def __init__(self, window: BuilderWindow):
        super().__init__(window)
        self.hostname: Gtk.ComboBoxText = self.build('ping_hostname')
        self.hostname.connect("changed", self.on_hostname_change)
        self.spinner: Gtk.Spinner = self.build('ping_spinner')
        self.host: Gtk.Button = self.build('ping_host')
        self.host_label: str = self.host.get_label()
        self.host.connect('activate', self.on_ping)
        self.host.connect('clicked', self.on_ping)
        self.result: Gtk.Image = self.build('ping_result')

    def on_hostname_change(self, *_) -> None:
        """Ping the set host."""
        self.result.set_from_icon_name(
            'face-plain-symbolic',
            Gtk.IconSize.LARGE_TOOLBAR
        )

    def on_ping(self, *args) -> None:
        """Ping the set host."""
        self.host.set_property('sensitive', False)
        self.hostname.set_property('sensitive', False)
        self.on_hostname_change(*args)
        self.host.set_label('')
        self.spinner.start()
        Thread(daemon=True, target=self.ping_thread).start()

    def ping_thread(self) -> None:
        """Ping the host."""
        try:
            ping(self.hostname.get_active_id())
        except CalledProcessError:
            success = False
        else:
            success = True

        GLib.idle_add(lambda: self.on_ping_completed(success))

    def on_ping_completed(self, success: bool) -> None:
        """Set the ping result."""
        self.spinner.stop()
        self.host.set_label(self.host_label)
        self.hostname.set_property('sensitive', True)
        self.host.set_property('sensitive', True)

        if success:
            self.result.set_from_icon_name(
                'face-smirk-symbolic',
                Gtk.IconSize.LARGE_TOOLBAR
            )
        else:
            self.result.set_from_icon_name(
                'face-sad-symbolic',
                Gtk.IconSize.LARGE_TOOLBAR
            )
