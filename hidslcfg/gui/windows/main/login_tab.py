"""Login window logic."""

from threading import Thread

from hidslcfg.exceptions import APIError
from hidslcfg.gui.api import GLib, Gtk, BuilderWindow, SubElement


__all__ = ['LoginTab']


class LoginTab(SubElement):
    """Login tab."""

    def __init__(self, window: BuilderWindow):
        super().__init__(window)
        self.user_name: Gtk.Entry = self.build('user_name')
        self.user_name.connect('activate', self.on_login)
        self.password: Gtk.Entry = self.build('password')
        self.password.connect('activate', self.on_login)
        self.login: Gtk.Button = self.build('login')
        self.login.connect('activate', self.on_login)
        self.login.connect('clicked', self.on_login)

    def on_login(self, *_) -> None:
        """Perform the login."""
        if not (user_name := self.user_name.get_text()):
            return self.show_error('Kein Benutzername angegeben.')

        if not (password := self.password.get_text()):
            return self.show_error('Kein Passwort angegeben.')

        Thread(
            daemon=True,
            target=self.login_thread,
            args=(user_name, password)
        ).start()

    def login_thread(self, user_name: str, password: str) -> None:
        """Login thread."""
        try:
            self.client.login(user_name, password)
        except APIError as api_error:
            error = str(api_error)
        else:
            error = None

        GLib.idle_add(lambda: self.on_login_done(error))

    def on_login_done(self, error: str | None) -> None:
        """Run after login is done."""
        if error:
            return self.show_error(error)

        self.next_window()
