"""Login window logic."""

from __future__ import annotations

from hidslcfg.api import Client
from hidslcfg.exceptions import APIError
from hidslcfg.gui.functions import get_asset
from hidslcfg.gui.gtk import Gdk, Gtk
from hidslcfg.gui.mixins import WindowMixin
from hidslcfg.gui.setup import SetupForm
from hidslcfg.gui.translation import translate


__all__ = ['LoginForm']


class LoginForm(WindowMixin):
    """Login form objects."""

    def __init__(self):
        """Create the login form."""
        builder = Gtk.Builder()
        builder.add_from_file(str(get_asset('login.glade')))
        self.window = builder.get_object('login')
        self.login_button = builder.get_object('login_button')
        self.user_name = builder.get_object('user_name')
        self.password = builder.get_object('password')
        builder.connect_signals(self.window)
        self.window.connect('destroy', Gtk.main_quit)
        self.login_button.connect('button-release-event', self.login)

    def login(self, caller: Gtk.Button, event: Gdk.EventButton) -> None:
        """Performs the login."""
        if not (user_name := self.user_name.get_text()):
            return self.show_error('Kein Benutzername angegeben.')

        if not (password := self.password.get_text()):
            return self.show_error('Kein Passwort angegeben.')

        client = Client()

        try:
            client.login(user_name, password)
        except APIError as error:
            return self.show_error(translate(error.json.get('message')))

        self.window.close()
        setup_form = SetupForm(client)
        setup_form.show()
