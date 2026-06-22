"""
Unit tests for interface_discovery.py

All subprocess / socket calls are mocked so these tests run identically
on any machine (including GitHub Actions runners) regardless of that
machine's actual network configuration.
"""

import subprocess
import unittest
from unittest.mock import patch

from interface_discovery import (
    calculate_network,
    discover_interface,
    get_default_route,
    get_interface_addresses,
)

SAMPLE_IP_ROUTE_OUTPUT = (
    "default via 192.168.1.1 dev eth0 proto dhcp metric 100\n"
    "192.168.1.0/24 dev eth0 proto kernel scope link src 192.168.1.10\n"
)

SAMPLE_IP_ADDR_OUTPUT = (
    "2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP\n"
    "    link/ether aa:bb:cc:dd:ee:ff brd ff:ff:ff:ff:ff:ff\n"
    "    inet 192.168.1.10/24 brd 192.168.1.255 scope global dynamic eth0\n"
)


class TestCalculateNetwork(unittest.TestCase):
    def test_24_bit_mask(self):
        self.assertEqual(calculate_network("192.168.1.10", 24), "192.168.1.0")

    def test_16_bit_mask(self):
        self.assertEqual(calculate_network("10.5.33.7", 16), "10.5.0.0")

    def test_32_bit_mask(self):
        self.assertEqual(calculate_network("8.8.8.8", 32), "8.8.8.8")


class TestGetDefaultRoute(unittest.TestCase):
    @patch("interface_discovery.run_command")
    def test_parses_gateway_and_interface(self, mock_run):
        mock_run.return_value = SAMPLE_IP_ROUTE_OUTPUT
        gateway, interface = get_default_route()
        self.assertEqual(gateway, "192.168.1.1")
        self.assertEqual(interface, "eth0")

    @patch("interface_discovery.run_command")
    def test_no_default_route_present(self, mock_run):
        mock_run.return_value = "192.168.1.0/24 dev eth0 proto kernel scope link\n"
        gateway, interface = get_default_route()
        self.assertIsNone(gateway)
        self.assertIsNone(interface)

    @patch("interface_discovery.run_command", side_effect=FileNotFoundError())
    def test_ip_command_missing(self, mock_run):
        gateway, interface = get_default_route()
        self.assertIsNone(gateway)
        self.assertIsNone(interface)

    @patch(
        "interface_discovery.run_command",
        side_effect=subprocess.CalledProcessError(1, ["ip", "route"]),
    )
    def test_ip_command_fails(self, mock_run):
        gateway, interface = get_default_route()
        self.assertIsNone(gateway)
        self.assertIsNone(interface)


class TestGetInterfaceAddresses(unittest.TestCase):
    @patch("interface_discovery.run_command")
    def test_parses_ip_and_cidr(self, mock_run):
        mock_run.return_value = SAMPLE_IP_ADDR_OUTPUT
        ip_address, cidr = get_interface_addresses("eth0")
        self.assertEqual(ip_address, "192.168.1.10")
        self.assertEqual(cidr, "192.168.1.0/24")

    @patch("interface_discovery.run_command")
    def test_no_inet_line_found(self, mock_run):
        mock_run.return_value = "2: eth0: <DOWN>\n"
        ip_address, cidr = get_interface_addresses("eth0")
        self.assertIsNone(ip_address)
        self.assertIsNone(cidr)


class TestDiscoverInterface(unittest.TestCase):
    @patch("interface_discovery.get_hostname", return_value="workstation01")
    @patch(
        "interface_discovery.get_interface_addresses",
        return_value=("192.168.1.10", "192.168.1.0/24"),
    )
    @patch(
        "interface_discovery.get_default_route",
        return_value=("192.168.1.1", "eth0"),
    )
    def test_full_discovery_happy_path(self, mock_route, mock_addr, mock_hostname):
        info = discover_interface()
        self.assertEqual(info.interface, "eth0")
        self.assertEqual(info.ip_address, "192.168.1.10")
        self.assertEqual(info.subnet_cidr, "192.168.1.0/24")
        self.assertEqual(info.gateway, "192.168.1.1")
        self.assertEqual(info.hostname, "workstation01")

    @patch("interface_discovery.get_default_route", return_value=(None, None))
    def test_raises_when_no_interface_found(self, mock_route):
        with self.assertRaises(RuntimeError):
            discover_interface()

    @patch("interface_discovery.get_interface_addresses", return_value=(None, None))
    @patch(
        "interface_discovery.get_default_route",
        return_value=("192.168.1.1", "eth0"),
    )
    def test_raises_when_no_ip_found(self, mock_route, mock_addr):
        with self.assertRaises(RuntimeError):
            discover_interface()


if __name__ == "__main__":
    unittest.main()
