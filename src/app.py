#!/usr/bin/env python3

import logging
import socket
from datetime import datetime
from ipaddress import IPv4Address

from flask import Flask, render_template
from zeroconf import ServiceBrowser, ServiceListener, Zeroconf

app = Flask(__name__)

# setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def discover_ssdp_devices(search_target="ssdp:all", timeout=5):
    """
    Discover SSDP devices on the local network

    Args:
        search_target: SSDP search target (default: "ssdp:all")
        timeout: How long to wait for responses (seconds)

    Returns:
        List of dictionaries containing device information
    """
    SSDP_ADDR = "239.255.255.250"
    SSDP_PORT = 1900

    # M-SEARCH message to discover SSDP devices
    ssdp_request = "\r\n".join(
        [
            "M-SEARCH * HTTP/1.1",
            f"HOST: {SSDP_ADDR}:{SSDP_PORT}",
            'MAN: "ssdp:discover"',
            "MX: 3",
            f"ST: {search_target}",
            "",
            "",
        ]
    )

    devices = []
    seen_locations = set()

    # Create UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.settimeout(timeout)

    try:
        # Send the M-SEARCH request
        sock.sendto(ssdp_request.encode(), (SSDP_ADDR, SSDP_PORT))
        logging.info(f"Sent SSDP discovery request for {search_target}")

        # Collect responses
        while True:
            try:
                data, addr = sock.recvfrom(2048)
                response = data.decode("utf-8", errors="ignore")

                # Parse the response to extract useful information
                device_info = {"ip": addr[0]}

                for line in response.split("\r\n"):
                    if ":" in line:
                        key, value = line.split(":", 1)
                        device_info[key.strip().lower()] = value.strip()

                # Use location as unique identifier to avoid duplicates
                location = device_info.get("location", f"{addr[0]}:{addr[1]}")
                if location not in seen_locations:
                    seen_locations.add(location)
                    devices.append(device_info)
                    logging.info(f"Found device at {addr[0]}")

            except socket.timeout:
                break

    except Exception as e:
        logging.error(f"Error during SSDP discovery: {e}")
    finally:
        sock.close()

    return devices


class MDNSListener(ServiceListener):
    """Listener for mDNS/Zeroconf services"""

    def __init__(self):
        self.devices = []

    def add_service(self, zc, type_, name):
        try:
            info = zc.get_service_info(type_, name)
            if info is None:
                logging.debug(f"No service info for {name}")
                return

            device_info = {
                "name": name,
                "type": type_,
                "ip": None,
                "addresses": [],
                "port": info.port,
                "server": info.server,
            }

            # Get IP addresses (handle multiple IPs)
            if info.addresses:
                for address in info.addresses:
                    try:
                        addr_str = socket.inet_ntoa(address)
                        device_info["addresses"].append(addr_str)
                    except Exception as e:
                        logging.error(f"Error converting address {address}: {e}")

                # Set primary IP to first address for backward compatibility
                if device_info["addresses"]:
                    device_info["ip"] = device_info["addresses"][0]

            # Get properties (handle both bytes and strings)
            if info.properties:
                device_info["properties"] = {}
                for k, v in info.properties.items():
                    try:
                        key_str = k.decode("utf-8") if isinstance(k, bytes) else k
                        value_str = (
                            v.decode("utf-8", errors="ignore")
                            if isinstance(v, bytes) and v
                            else ""
                        )
                        device_info["properties"][key_str] = value_str
                    except Exception as e:
                        logging.error(f"Error decoding property {k}: {e}")

            self.devices.append(device_info)
            logging.info(f"Found mDNS device: {name}")
        except Exception as ex:
            logging.error(f"Error processing service {name}: {ex}")

    def remove_service(self, zc, type_, name):
        pass

    def update_service(self, zc, type_, name):
        pass


def discover_mdns_devices(timeout=5):
    """
    Discover mDNS devices on the local network

    Args:
        timeout: How long to wait for responses (seconds)

    Returns:
        List of dictionaries containing device information
    """
    zeroconf = Zeroconf()
    listener = MDNSListener()

    # Common service types to browse
    # fmt: off
    service_types = [
        "_afpovertcp._tcp.local.",            # AppleTalk Filing Protocol (AFP)
        "_airdrop._tcp.local.",               # Apple AirDrop
        "_airplay._tcp.local.",               # Apple AirPlay (Apple TV)
        "_airport._tcp.local.",               # Apple AirPort
        "_androidtvremote._tcp.local.",       # Nvidia Shield / Android TV
        "_axis-video._tcp.local.",            # Axis cameras
        "_bose._tcp.local.",                  # Bose speakers
        "_companion-link._tcp.local.",        # Apple TV remote
        "_cups._sub._ipps._tcp.local.",       # Printers (CUPS)
        "_daap._tcp.local.",                  # Apple iTunes music sharing
        "_device-info._tcp.local.",           # Apple device info
        "_epson-scanner._tcp.local.",         # Epson scanners
        "_ftp._tcp.local.",                   # FTP
        "_googlecast._tcp.local.",            # Google Cast (Chromecast)
        "_googlezone._tcp.local.",            # Google Home
        "_hap._tcp.local.",                   # Apple HomeKit Accessory Protocol
        "_homekit._tcp.local.",               # Apple HomeKit
        "_http._tcp.local.",                  # HTTP
        "_https._tcp.local.",                 # HTTPS
        "_hue._tcp.local.",                   # Philips Hue bridge
        "_ipp._tcp.local.",                   # Printers (Internet Printing Protocol)
        "_ipps._tcp.local.",                  # Printers (IPP over TLS)
        "_matter._tcp.local.",                # Matter smart home protocol
        "_mqtt._tcp.local.",                  # MQTT broker
        "_nfs._tcp.local.",                   # Network File System
        "_nut._tcp.local.",                   # Network UPS Tools
        "_pdl-datastream._tcp.local.",        # Printers (Apple Page Description Language)
        "_philipshue._tcp.local.",            # Philips Hue lights
        "_printer._tcp.local.",               # Printers
        "_raop._tcp.local.",                  # Apple AirPlay audio (AirTunes)
        "_remote-login._tcp.local.",          # Remote login
        "_rfb._tcp.local.",                   # VNC (Remote Frame Buffer)
        "_roku._tcp.local.",                  # Roku streaming devices
        "_rsp._tcp.local.",                   # Roku streaming player
        "_scanner._tcp.local.",               # Scanners
        "_sftp-ssh._tcp.local.",              # SFTP
        "_shelly._tcp.local.",                # Shelly IoT devices
        "_sleep-proxy._udp.local.",           # Apple Bonjour sleep proxy
        "_smb._tcp.local.",                   # SMB/Samba file sharing
        "_sonos._tcp.local.",                 # Sonos speakers
        "_spotify-connect._tcp.local.",       # Spotify Connect
        "_ssh._tcp.local.",                   # SSH
        "_telnet._tcp.local.",                # Telnet
        "_webdav._tcp.local.",                # WebDAV
        "_webdavs._tcp.local.",               # WebDAV
        "_workstation._tcp.local.",           # Workstation service
    ]

    browsers = []
    try:
        logging.info("Starting mDNS discovery")
        for service_type in service_types:
            browser = ServiceBrowser(zeroconf, service_type, listener)
            browsers.append(browser)

        # Wait for discoveries
        import time

        time.sleep(timeout)

    except Exception as e:
        logging.error(f"Error during mDNS discovery: {e}")
    finally:
        zeroconf.close()

    return listener.devices


def ip_sort_key(device):
    """
    Return an IPv4Address for sorting devices by IP address.
    Devices without valid IPs are sorted to the end.

    Args:
        device: Dictionary containing device information with optional 'ip' key

    Returns:
        IPv4Address object for sorting
    """
    ip = device.get("ip", "")
    if ip:
        try:
            return IPv4Address(ip)
        except Exception as e:
            logging.warning(f"Invalid IP address '{ip}': {e}")
            return IPv4Address("255.255.255.255")  # Put invalid IPs at the end
    return IPv4Address("255.255.255.255")  # Put devices without IP at the end


@app.route("/")
def index():
    """Serve the main page with discovered devices"""
    ssdp_devices = discover_ssdp_devices(timeout=5)
    mdns_devices = discover_mdns_devices(timeout=5)

    # Sort devices by IP address
    ssdp_devices.sort(key=ip_sort_key)
    mdns_devices.sort(key=ip_sort_key)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return render_template(
        "index.html",
        ssdp_devices=ssdp_devices,
        mdns_devices=mdns_devices,
        timestamp=timestamp,
    )
