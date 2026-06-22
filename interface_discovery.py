"""
interface_discovery.py

Phase 1 of NetMapper: identifies the local network configuration.

Determines:
    - the active network interface
    - the local IPv4 address
    - the subnet (CIDR notation)
    - the default gateway
    - the local hostname

Uses the Linux `ip` command (via subprocess) plus the stdlib `socket`
module. No third-party dependencies.
"""

from __future__ import annotations

import re
import socket
import subprocess
from dataclasses import asdict, dataclass
from typing import Optional


@dataclass
class InterfaceInfo:
    """Structured result of a Phase 1 discovery run."""

    interface: str
    ip_address: str
    subnet_cidr: str
    gateway: Optional[str]
    hostname: str

    def to_dict(self) -> dict:
        return asdict(self)


def run_command(cmd: list[str]) -> str:
    """
    Run a system command and return its stdout as text.

    Raises subprocess.CalledProcessError if the command exits non-zero,
    or FileNotFoundError if the command isn't installed.
    """
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return result.stdout


def get_default_route() -> tuple[Optional[str], Optional[str]]:
    """
    Parse `ip route` to find the default gateway and the interface
    used for the default route.

    Returns:
        (gateway_ip, interface_name) -- either may be None if not found
        or if the `ip` command is unavailable.
    """
    try:
        output = run_command(["ip", "route"])
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None, None

    for line in output.splitlines():
        if line.startswith("default"):
            match = re.search(r"default via (\S+) dev (\S+)", line)
            if match:
                return match.group(1), match.group(2)

    return None, None


def get_interface_addresses(interface: str) -> tuple[Optional[str], Optional[str]]:
    """
    Parse `ip addr show <interface>` to extract the IPv4 address and the
    CIDR network for that interface.

    Returns:
        (ip_address, cidr_subnet) -- either may be None if not found.
    """
    try:
        output = run_command(["ip", "addr", "show", interface])
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None, None

    match = re.search(r"inet (\d+\.\d+\.\d+\.\d+)/(\d+)", output)
    if not match:
        return None, None

    ip_address = match.group(1)
    prefix_len = int(match.group(2))
    network = calculate_network(ip_address, prefix_len)
    cidr = f"{network}/{prefix_len}"

    return ip_address, cidr


def calculate_network(ip_address: str, prefix_len: int) -> str:
    """Compute the network address for an IP address and prefix length."""
    octets = [int(o) for o in ip_address.split(".")]
    ip_int = (octets[0] << 24) + (octets[1] << 16) + (octets[2] << 8) + octets[3]
    mask = (0xFFFFFFFF << (32 - prefix_len)) & 0xFFFFFFFF
    network_int = ip_int & mask

    return ".".join(
        str((network_int >> shift) & 0xFF) for shift in (24, 16, 8, 0)
    )


def get_hostname() -> str:
    """Return the local machine's hostname."""
    try:
        return socket.gethostname()
    except OSError:
        return "unknown"


def discover_interface() -> InterfaceInfo:
    """
    Main entry point for Phase 1.

    Raises:
        RuntimeError if the default interface or its IP address cannot
        be determined (e.g. no network connection, or `ip` not installed).
    """
    gateway, interface = get_default_route()

    if interface is None:
        raise RuntimeError(
            "Could not determine the default network interface. "
            "Confirm you are connected to a network and that the `ip` "
            "command (iproute2) is installed."
        )

    ip_address, cidr = get_interface_addresses(interface)

    if ip_address is None:
        raise RuntimeError(
            f"Could not determine an IPv4 address for interface '{interface}'."
        )

    return InterfaceInfo(
        interface=interface,
        ip_address=ip_address,
        subnet_cidr=cidr,
        gateway=gateway,
        hostname=get_hostname(),
    )


if __name__ == "__main__":
    info = discover_interface()
    print(f"Interface: {info.interface}")
    print(f"IP Address: {info.ip_address}")
    print(f"Subnet: {info.subnet_cidr}")
    print(f"Gateway: {info.gateway}")
    print(f"Hostname: {info.hostname}")
