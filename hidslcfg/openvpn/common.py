"""Common constants for the OpenVPN subsystem."""

from ipaddress import IPv4Address
from pathlib import Path


__all__ = ["CLIENT_DIR", "DEFAULT_SERVICE", "SERVER"]


CLIENT_DIR = Path("/etc/openvpn/client")
DEFAULT_SERVICE = "openvpn-client@terminals.service"
SERVER = IPv4Address("10.8.0.1")
