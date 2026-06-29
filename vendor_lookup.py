"""
vendor_lookup.py

Phase 5 of NetMapper: identifies device manufacturers from MAC addresses.

Uses the mac-vendor-lookup library which queries the OUI database
to map MAC address prefixes to vendor names.

Install: pip install mac-vendor-lookup
"""

from __future__ import annotations

from mac_vendor_lookup import MacLookup, VendorNotFoundError


def lookup_vendor(mac_address: str) -> str:
    """
    Look up the vendor name for a given MAC address.

    Args:
        mac_address: e.g. 'aa:bb:cc:dd:ee:ff'

    Returns:
        Vendor name string if found, empty string if not.
    """
    try:
        return MacLookup().lookup(mac_address)
    except (VendorNotFoundError, ValueError):
        return ""


def enrich_vendors(devices: list) -> None:
    """
    Look up vendor for all devices that have a MAC address.

    Modifies devices in place.
    Skips devices with no MAC address.
    """
    mac_lookup = MacLookup()

    for device in devices:
        if not device.mac_address:
            continue

        try:
            device.vendor = mac_lookup.lookup(device.mac_address)
            print(f"  {device.ip_address:<18} {device.mac_address}  -> {device.vendor}")
        except (VendorNotFoundError, ValueError):
            print(f"  {device.ip_address:<18} {device.mac_address}  -> vendor unknown")


if __name__ == "__main__":
    from net_scanner import scan_network
    from interface_discovery import discover_interface
    from arp_collector import collect_arp, enrich_devices

    info = discover_interface()
    devices = scan_network(info.subnet_cidr)
    arp_entries = collect_arp()
    enrich_devices(devices, arp_entries)

    print(f"Looking up vendors for {len(devices)} device(s)...\n")
    enrich_vendors(devices)

