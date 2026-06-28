"""
hostname_resolver.py

Phase 4 of NetMapper: resolves hostnames for discovered devices.

Uses socket.gethostbyaddr() from the standard library to perform
reverse DNS lookups on each IP address found in Phase 2.

No third-party dependencies. No sudo required.
"""

from __future__ import annotations

import socket


def resolve_hostname(ip_address: str, timeout: int = 3) -> str:
    """
    Perform a reverse DNS lookup on a single IP address.

    Args:
        ip_address: IP to look up e.g. '192.168.1.1'
        timeout:    seconds before giving up. Default 3.

    Returns:
        Hostname string if found, empty string if not.
    """
    old_timeout = socket.getdefaulttimeout()
    try:
        socket.setdefaulttimeout(timeout)
        hostname, _, _ = socket.gethostbyaddr(ip_address)
        return hostname
    except (socket.herror, socket.gaierror, socket.timeout):
        return ""
    finally:
        socket.setdefaulttimeout(old_timeout)


def resolve_all_hostnames(devices: list) -> None:
    """
    Resolve hostnames for all devices in place.

    Skips devices that already have a hostname.
    Skips devices where lookup fails — hostname stays empty string.

    Args:
        devices: list of Device objects from Phase 2.
    """
    for device in devices:
        if device.hostname:
            continue

        hostname = resolve_hostname(device.ip_address)
        if hostname:
            device.hostname = hostname
            print(f"  {device.ip_address:<18} -> {hostname}")
        else:
            print(f"  {device.ip_address:<18} -> no hostname found")


if __name__ == "__main__":
    from net_scanner import scan_network
    from interface_discovery import discover_interface

    info = discover_interface()
    devices = scan_network(info.subnet_cidr)

    print(f"Resolving hostnames for {len(devices)} device(s)...\n")
    resolve_all_hostnames(devices)
