"""Login window definitions."""

from __future__ import annotations
from typing import NamedTuple

from hidslcfg.gui.functions import get_asset
from hidslcfg.gui.gtk import Gdk, Gtk


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

    def login(self, caller: Gtk.Button, event: Gdk.EventButton) -> None:
        """Performs the login."""
        print('Logging in with:', self.user_name.get_text(), '/',
              self.password.get_text())
