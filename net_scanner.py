"""
net_scanner.py

Phase 2 of NetMapper: discovers live hosts on the local subnet.

Uses nmap -sn (ping scan, no port scan) via subprocess to sweep the
subnet returned by Phase 1 and returns a list of Device objects.

Each Device starts with only an IP address populated. Later phases
(ARP, hostname resolution, vendor lookup, service scan) enrich the
same Device objects with additional fields.
"""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass, field
from datetime import datetime

from interface_discovery import discover_interface


@dataclass
class Device:
    """
    Represents a single network device discovered during scanning.

    Fields are populated incrementally across phases:
        Phase 2  - ip_address, last_seen
        Phase 3  - mac_address (ARP)
        Phase 4  - hostname
        Phase 5  - vendor
        Phase 6  - os, open_ports, services
    """

    ip_address: str
    mac_address: str = ""
    hostname: str = ""
    vendor: str = ""
    os: str = ""
    open_ports: list = field(default_factory=list)
    services: list = field(default_factory=list)
    device_type: str = "unknown"
    last_seen: str = ""

    def to_dict(self) -> dict:
        return {
            "ip_address": self.ip_address,
            "mac_address": self.mac_address,
            "hostname": self.hostname,
            "vendor": self.vendor,
            "os": self.os,
            "open_ports": self.open_ports,
            "services": self.services,
            "device_type": self.device_type,
            "last_seen": self.last_seen,
        }


def parse_nmap_output(raw_output: str) -> list[Device]:
    """
    Parse raw nmap -sn output and return a list of Device objects.

    Nmap reports live hosts with lines like:
        Nmap scan report for 192.168.1.1
        Nmap scan report for hostname (192.168.1.10)

    Both formats are handled. The hostname format extracts the IP
    from inside the parentheses.
    """
    devices = []
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    ip_pattern = re.compile(
        r"Nmap scan report for (?:\S+ \()?(\d+\.\d+\.\d+\.\d+)\)?"
    )

    for match in ip_pattern.finditer(raw_output):
        ip = match.group(1)
        devices.append(Device(ip_address=ip, last_seen=timestamp))

    return devices


def scan_network(subnet: str, timeout: int = 120) -> list[Device]:
    """
    Discover live hosts on the given subnet using nmap -sn.

    Args:
        subnet:  CIDR notation subnet, e.g. '192.168.1.0/24'.
                 Comes from InterfaceInfo.subnet_cidr (Phase 1).
        timeout: Maximum seconds to wait for nmap to finish.
                 Defaults to 120 seconds. Raises subprocess.TimeoutExpired
                 if exceeded.

    Returns:
        List of Device objects, one per live host found.
        Returns an empty list if nmap finds nothing or fails.
    """
    try:
        result = subprocess.run(
            ["nmap", "-sn", subnet],
            capture_output=True,
            text=True,
            check=True,
            timeout=timeout,
        )
    except FileNotFoundError:
        print("[net_scanner] ERROR: nmap is not installed. Run: sudo apt install nmap")
        return []
    except subprocess.TimeoutExpired:
        print(f"[net_scanner] ERROR: nmap timed out after {timeout}s on subnet {subnet}")
        return []
    except subprocess.CalledProcessError as e:
        print(f"[net_scanner] ERROR: nmap exited with error: {e.stderr.strip()}")
        return []

    return parse_nmap_output(result.stdout)


if __name__ == "__main__":
    info = discover_interface()
    print(f"Scanning {info.subnet_cidr}...\n")

    devices = scan_network(info.subnet_cidr)

    if not devices:
        print("No devices found.")
    else:
        for device in devices:
            print(f"Found: {device.ip_address}  (last seen: {device.last_seen})")


