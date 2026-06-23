import subprocess
import re
from interface_discovery import discover_interface


def scan_network(subnet: str) -> list:
    result = subprocess.run(
        ["nmap", "-sn", subnet],
        capture_output=True,
        text=True,
        check=True
    )

    hosts = re.findall(r"Nmap scan report for (\d+\.\d+\.\d+\.\d+)", result.stdout)
    return hosts

    result1 = subprocess.run(
        ["ip", "addr"],
        capture_output=True,
        text=True,
        check=True
    )
    print(result1.stdout)

    result2 = subprocess.run(
        ["ip", "route"],
        capture_output=True,
        text=True,
        check=True
    )
    print(result2.stdout)


if __name__ == "__main__":
    info = discover_interface()
    hosts = scan_network(info.subnet_cidr)
    for host in hosts:
        print(f"Found: {host}")
