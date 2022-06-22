"""Login window logic."""

from hidslcfg.api import Client
from hidslcfg.exceptions import APIError
from hidslcfg.gui.functions import get_asset
from hidslcfg.gui.gtk import Gtk
from hidslcfg.gui.mixins import WindowMixin
from hidslcfg.gui.setup import SetupForm


__all__ = ['LoginForm']


class LoginForm(WindowMixin):
    """Login form objects."""

    def __init__(self):
        """Create the login form."""
        self.client = Client()
        self.logged_in = False
        builder = Gtk.Builder()
        builder.add_from_file(str(get_asset('login.glade')))
        self.window = builder.get_object('login')
        self.login_button = builder.get_object('login_button')
        self.user_name = builder.get_object('user_name')
        self.password = builder.get_object('password')
        builder.connect_signals(self.window)
        self.window.connect('destroy', self.on_destroy)
        self.login_button.connect('button-press-event', self.on_login)

    def on_destroy(self, *_) -> None:
        """Handle window destruction events."""
        if self.logged_in:
            setup_form = SetupForm(self.client)
            setup_form.show()
        else:
            Gtk.main_quit()

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

        self.logged_in = True
        self.window.destroy()
