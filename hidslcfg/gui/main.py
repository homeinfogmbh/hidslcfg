"""Main GUI application."""

from sys import argv

from hidslcfg.gui.application import Application


def main() -> int:
    """Starts the GUI."""

    return Application().run(argv)


if __name__ == '__main__':
    main()
