"""Login window logic."""

from hidslcfg.exceptions import APIError
from hidslcfg.gui.builder_window import BuilderWindow
from hidslcfg.gui.sub_element import SubElement
from hidslcfg.gui.gtk import Gtk


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

        try:
            self.client.login(user_name, password)
        except APIError as error:
            return self.show_error(str(error))

        self.next_window()
