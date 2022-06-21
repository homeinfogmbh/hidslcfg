"""Message translation."""


__all__ = ['translate']


TRANSLATIONS = {
    'Invalid credentials.': 'Ungültige Anmeldedaten.'
}


def translate(text: str | None) -> str:
    """Translates the given message."""

    return TRANSLATIONS.get(text, text or 'NO_TEXT')
