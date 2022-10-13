"""Wi-Fi setup functions."""

from functools import partial
from pathlib import Path
from re import fullmatch, match
from subprocess import PIPE, CalledProcessError, check_output
from typing import Iterable, Iterator

from netifaces import interfaces

from hidslcfg.common import SYSTEMD_NETWORKD
from hidslcfg.magic_usb import MagicUSBKey
from hidslcfg.system import systemctl


__all__ = [
    'MAX_PSK_LEN',
    'MIN_PSK_LEN',
    'configure',
    'disable',
    'from_magic_usb_key',
    'list_wifi_interfaces',
    'load_wifi_configs'
]


CONFIG_DIR = Path('/etc/wpa_supplicant')
CONFIG_FILE_TEMPLATE = 'wpa_supplicant-{interface}.conf'
CONFIG_FILE_REGEX = CONFIG_FILE_TEMPLATE.format(interface='(.+)')
KEYS = ('ssid', 'psk')
MAGIC_FILE_NAME = 'wifi.txt'
MAX_PSK_LEN = 63
MIN_PSK_LEN = 8
SERVICE_TEMPLATE = 'wpa_supplicant@{interface}.service'
WIFI_INTERFACE_REGEX = r'^wlp'
WPA_CONFIG_PARSER = {
    'ssid':  r'^\s*ssid="(.+)"$',
    'psk': r'^\s*#psk="(.+)"$',
    'psk_encoded': r'^\s*psk=(.+)$'
}


def configure(interface: str, ssid: str, psk: str):
    """Configure the given interface for WPA."""

    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    filename = CONFIG_DIR / CONFIG_FILE_TEMPLATE.format(interface=interface)

    with filename.open('w') as file:
        file.write(wpa_passphrase(ssid, psk))

    start_and_enable(SERVICE_TEMPLATE.format(interface=interface))
    systemctl('restart', SYSTEMD_NETWORKD)


def disable(interfaces_to_disable: Iterable[str]) -> None:
    """Remove configuration for the given interfaces."""

    for interface in interfaces_to_disable:
        stop_and_disable(SERVICE_TEMPLATE.format(interface=interface))


def from_magic_usb_key(*, filename: str = MAGIC_FILE_NAME) -> dict[str, str]:
    """Load a wpa_supplicant configuration from the magic USB key."""

    with MagicUSBKey() as mountpoint:
        with (mountpoint / filename).open('r', encoding='utf-8') as file:
            return {
                key: value for key, value in zip(KEYS, map(str.rstrip, file))
            }


def list_wifi_interfaces() -> Iterator[str]:
    """Yield available WiFi interfaces."""

    return filter(partial(match, WIFI_INTERFACE_REGEX), interfaces())


def load_wifi_configs() -> dict[str, dict[str, str]]:
    """Load wpa_supplicant configuration files."""

    configs = {}

    for file in iter_wifi_configs():
        if regex_match := fullmatch(CONFIG_FILE_REGEX, file.name):
            configs[regex_match.group(1)] = load_wifi_config(file)

    return configs


def iter_wifi_configs() -> Iterator[Path]:
    """Yield paths to available wpa_supplicant configuration files."""

    return CONFIG_DIR.glob(CONFIG_FILE_TEMPLATE.format(interface='*'))


def load_wifi_config(file: Path) -> dict[str, str]:
    """Load wpa_supplicant config file."""

    config = {}

    with file.open('r', encoding='utf-8') as file:
        for line in file:
            for key, regex in WPA_CONFIG_PARSER.items():
                if regex_match := fullmatch(regex, line.strip()):
                    config[key] = regex_match.group(1)
                    continue

    return config


def wpa_passphrase(ssid: str, psk: str) -> str:
    """Invoke wpa_passphrase."""

    return check_output(
        ['/usr/bin/wpa_passphrase', ssid, psk],
        stderr=PIPE,
        text=True
    )


def start_and_enable(service: str) -> None:
    """Start and enable wpa_supplicant for the respective interface."""

    try:
        systemctl('is-enabled', service)
    except CalledProcessError:
        systemctl('enable', service)

    try:
        systemctl('is-active', service)
    except CalledProcessError:
        systemctl('start', service)
    else:
        systemctl('restart', service)


def stop_and_disable(service: str) -> None:
    """Stop and disable wpa_supplicant for the respective interface."""

    systemctl('disable', '--now', service)
