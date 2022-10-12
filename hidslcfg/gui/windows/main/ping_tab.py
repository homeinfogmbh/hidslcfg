"""Login window logic."""

from subprocess import CalledProcessError
from threading import Thread

from hidslcfg.gui.api import Gtk, BuilderWindow, SubElement
from hidslcfg.system import ping


__all__ = ['PingTab']


class PingTab(SubElement):
    """Ping test tab."""

    def __init__(self, window: BuilderWindow):
        super().__init__(window)
        self.ping_successful: bool | None = None
        self.ping_hostname: Gtk.ComboBoxText = self.build('ping_hostname')
        self.ping_hostname.connect("changed", self.on_ping_hostname_change)
        self.ping_spinner: Gtk.Spinner = self.build('ping_spinner')
        self.ping_host: Gtk.Button = self.build('ping_host')
        self.ping_host_label: str = self.ping_host.get_label()
        self.ping_host.connect('activate', self.on_ping_host)
        self.ping_host.connect('clicked', self.on_ping_host)
        self.ping_result: Gtk.Image = self.build('ping_result')
        self.new_signal('ping-host-completed', self.on_ping_completed)

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

    def ping_thread(self) -> None:
        """Ping the host."""
        try:
            ping(self.ping_hostname.get_active_id())
        except CalledProcessError:
            self.ping_successful = False
        else:
            self.ping_successful = True

        self.window.emit('ping-host-completed', None)

    def on_ping_completed(self, *_) -> None:
        """Set the ping result."""
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
