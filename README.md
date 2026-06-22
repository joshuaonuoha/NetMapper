# NetMapper

Automated network discovery, inventory, and topology visualization for
Linux. NetMapper combines active scanning (Nmap), passive packet
analysis (TShark), and graph theory (NetworkX) to answer the basic
questions every network admin eventually asks: *what's on my network,
and what's it doing?*

> **Status:** early development, built one phase at a time.
> Phase 1 (Interface Discovery) is implemented. See [Roadmap](#roadmap).

[![CI](https://github.com/YOUR_USERNAME/netmapper/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/netmapper/actions/workflows/ci.yml)

## What it does (when finished)

- Discovers every reachable device on a local network
- Pulls IP/MAC addresses, hostnames, vendors, OS, and open ports per device
- Captures traffic to infer which devices talk to which
- Builds a topology graph and renders it as an image
- Exports the full inventory to an Excel workbook

## Requirements

- Linux (uses `ip`, `arp`/`ip neigh`, `nmap`, `tshark`)
- Python 3.10+
- Root/sudo for packet capture phases (not needed for Phase 1)

## Installation

```bash
git clone https://github.com/YOUR_USERNAME/netmapper.git
cd netmapper

python3 -m venv venv
source venv/bin/activate

pip install -r requirements-dev.txt   # includes runtime deps + pytest/flake8
```

## Usage

```bash
python3 main.py
```

Current (Phase 1) output:

```
=== NetMapper ===
Phase 1: Discovering local network interface...

Interface:   eth0
IP Address:  192.168.1.10
Subnet:      192.168.1.0/24
Gateway:     192.168.1.1
Hostname:    workstation01
```

## Running tests

```bash
pytest tests/ -v
flake8 . --max-line-length=100
```

Both are also run automatically in CI on every push/PR — see
[`.github/workflows/ci.yml`](.github/workflows/ci.yml).

## Project structure

```
netmapper/
├── main.py                   # entry point / controller
├── interface_discovery.py    # Phase 1 - local interface, IP, gateway
├── network_scanner.py        # Phase 2 - planned
├── arp_collector.py          # Phase 3 - planned
├── nmap_scanner.py           # Phase 6 - planned
├── packet_analyzer.py        # Phase 7 - planned
├── topology_builder.py       # Phase 9 - planned
├── excel_exporter.py         # Phase 10 - planned
├── graph_visualizer.py       # Phase 9 - planned
├── tests/
│   └── test_interface_discovery.py
├── requirements.txt
├── requirements-dev.txt
└── .github/workflows/ci.yml
```

## Roadmap

- [x] Phase 1 — Interface Discovery
- [ ] Phase 2 — Network Discovery (Nmap host sweep)
- [ ] Phase 3 — ARP Data Collection
- [ ] Phase 4 — Hostname Resolution
- [ ] Phase 5 — Vendor Identification (MAC OUI lookup)
- [ ] Phase 6 — Detailed Device Analysis (`nmap -A`)
- [ ] Phase 7 — Packet Capture & Traffic Analysis (TShark)
- [ ] Phase 8 — Dependency Mapping
- [ ] Phase 9 — Network Graph Construction (NetworkX + matplotlib)
- [ ] Phase 10 — Spreadsheet Generation (pandas + openpyxl)

Further out: scheduled/continuous monitoring, rogue device alerts,
historical tracking, and a Flask dashboard.

## Contributing / workflow

Each phase is built on its own branch and merged once CI is green:

```bash
git checkout -b feature/phase-2-network-scanner
# ... implement + test ...
git push -u origin feature/phase-2-network-scanner
# open a PR into main, let CI run, then merge
```

## License

MIT (add a `LICENSE` file before making the repo public, if you want
this license).
