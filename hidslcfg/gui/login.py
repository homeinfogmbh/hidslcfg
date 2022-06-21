"""Login window definitions."""

from __future__ import annotations
from typing import NamedTuple

from hidslcfg.api import Client
from hidslcfg.exceptions import APIError
from hidslcfg.gui.functions import get_asset
from hidslcfg.gui.gtk import Gdk, Gtk
from hidslcfg.gui.translation import translate


__all__ = ['LoginForm']


class LoginForm(NamedTuple):
    """Login form objects."""

    window: Gtk.ApplicationWindow
    login_button: Gtk.Button
    user_name: Gtk.Entry
    password: Gtk.Entry

    @classmethod
    def create(cls) -> LoginForm:
        """Create the login form."""
        builder = Gtk.Builder()
        builder.add_from_file(str(get_asset('login.glade')))
        window = builder.get_object('login')
        login_button = builder.get_object('login_button')
        user_name = builder.get_object('user_name')
        password = builder.get_object('password')
        builder.connect_signals(window)
        return cls(window, login_button, user_name, password)

    def show_error(self, message: str) -> None:
        """Shows an error message."""
        message_dialog = Gtk.MessageDialog(
            transient_for=self.window,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text=message
        )
        message_dialog.run()
        message_dialog.destroy()

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

