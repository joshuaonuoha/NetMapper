"""
main.py

NetMapper - Automated Network Discovery and Topology Visualization System
Main controller / entry point.

Currently implemented:
    Phase 1 - Interface Discovery  (interface_discovery.py)
    Phase 2 - Network Discovery    (net_scanner.py)

Planned, one phase per feature branch:
    Phase 3  - ARP Data Collection       (arp_collector.py)
    Phase 4  - Hostname Resolution
    Phase 5  - Vendor Identification
    Phase 6  - Detailed Device Analysis  (service_scanner.py)
    Phase 7  - Packet Capture & Traffic  (packet_analyzer.py)
    Phase 8  - Dependency Mapping
    Phase 9  - Network Graph             (topology_builder.py / graph_visualizer.py)
    Phase 10 - Spreadsheet Generation    (excel_exporter.py)
"""

from interface_discovery import discover_interface
from net_scanner import scan_network


def main() -> None:
    print("=== NetMapper ===")

    # ── Phase 1: Interface Discovery ─────────────────────────────────────────
    print("Phase 1: Discovering local network interface...\n")
    info = discover_interface()

    print(f"Interface:   {info.interface}")
    print(f"IP Address:  {info.ip_address}")
    print(f"Subnet:      {info.subnet_cidr}")
    print(f"Gateway:     {info.gateway}")
    print(f"Hostname:    {info.hostname}")

    # ── Phase 2: Network Discovery ───────────────────────────────────────────
    print("\nPhase 2: Scanning network for live hosts...\n")
    devices = scan_network(info.subnet_cidr)

    if not devices:
        print("  No devices found.")
    else:
        print(f"  Found {len(devices)} device(s):\n")
        for device in devices:
            print(f"  {device.ip_address:<18} last seen: {device.last_seen}")


if __name__ == "__main__":
    main()

