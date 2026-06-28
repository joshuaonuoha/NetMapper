"""
arp_collector.py

Phase 3 of NetMapper: collects the local ARP/neighbor table.

Uses `ip neigh` via subprocess to read every IP-to-MAC mapping
the system currently knows about. Results are used to enrich
Device objects from Phase 2 with MAC addresses.

No third-party dependencies. No sudo required.
"""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass


@dataclass
class ARPEntry:
    """A single entry from the ARP/neighbor table."""

    ip_address: str
    mac_address: str
    interface: str
    state: str


def parse_ip_neigh(raw_output: str) -> list[ARPEntry]:
    """
    Parse raw `ip neigh` output into ARPEntry objects.

    Example input line:
        192.168.1.1 dev eth0 lladdr aa:bb:cc:dd:ee:ff REACHABLE
    """
    entries = []

    pattern = re.compile(
        r"(\d+\.\d+\.\d+\.\d+)\s+dev\s+(\S+)\s+lladdr\s+"
        r"([0-9a-fA-F:]{17})\s+(\S+)"
    )

    for match in pattern.finditer(raw_output):
        entries.append(ARPEntry(
            ip_address=match.group(1),
            interface=match.group(2),
            mac_address=match.group(3),
            state=match.group(4),
        ))

    return entries


def collect_arp(timeout: int = 30) -> list[ARPEntry]:
    """
    Run `ip neigh` and return parsed ARP entries.

    Args:
        timeout: max seconds to wait. Default 30.

    Returns:
        List of ARPEntry objects. Empty list on failure.
    """
    try:
        result = subprocess.run(
            ["ip", "neigh"],
            capture_output=True,
            text=True,
            check=True,
            timeout=timeout,
        )
    except FileNotFoundError:
        print("[arp_collector] ERROR: ip command not found. Install iproute2.")
        return []
    except subprocess.TimeoutExpired:
        print(f"[arp_collector] ERROR: ip neigh timed out after {timeout}s")
        return []
    except subprocess.CalledProcessError as e:
        print(f"[arp_collector] ERROR: {e.stderr.strip()}")
        return []

    return parse_ip_neigh(result.stdout)


def enrich_devices(devices: list, arp_entries: list[ARPEntry]) -> None:
    """
    Match ARP entries to Device objects by IP and fill in MAC address.

    Modifies devices in place.
    """
    arp_map = {entry.ip_address: entry for entry in arp_entries}

    for device in devices:
        if device.ip_address in arp_map:
            device.mac_address = arp_map[device.ip_address].mac_address


if __name__ == "__main__":
    entries = collect_arp()

    if not entries:
        print("No ARP entries found.")
    else:
        print(f"Found {len(entries)} ARP entries:\n")
        for e in entries:
            print(f"  {e.ip_address:<18} {e.mac_address}  {e.state}")