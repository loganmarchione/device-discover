from ipaddress import IPv4Address

from src.app import discover_mdns_devices, discover_ssdp_devices, ip_sort_key

################################################################################
# tests for `ip_sort_key`
################################################################################


def test_ip_sort_key_valid_ip():
    """Test with a valid IP address"""
    device = {"ip": "192.168.1.10"}
    result = ip_sort_key(device)
    print(f"\nResult: {result}")
    assert result == IPv4Address("192.168.1.10")


def test_ip_sort_key_missing_ip():
    """Test with a device that has no IP field"""
    device = {"name": "test-device"}
    result = ip_sort_key(device)
    print(f"\nResult: {result}")
    assert result == IPv4Address("255.255.255.255")


def test_ip_sort_key_invalid_ip():
    """Test with an invalid IP address string"""
    device = {"ip": "not-an-ip"}
    result = ip_sort_key(device)
    print(f"\nResult: {result}")
    assert result == IPv4Address("255.255.255.255")


def test_ip_sort_key_empty_string():
    """Test with an empty IP string"""
    device = {"ip": ""}
    result = ip_sort_key(device)
    print(f"\nResult: {result}")
    assert result == IPv4Address("255.255.255.255")


def test_sorting_devices_by_ip():
    """Test that devices are sorted correctly by IP"""
    devices = [
        {"ip": "192.168.1.10", "name": "device1"},
        {"ip": "192.168.1.2", "name": "device2"},
        {"ip": "10.0.0.1", "name": "device3"},
        {"ip": "", "name": "device4"},  # Empty IP string
        {"name": "device5"},  # No IP field
    ]

    sorted_devices = sorted(devices, key=ip_sort_key)

    # Print for debugging
    print("")
    for i, device in enumerate(sorted_devices):
        print(f"Position {i}: {device}")

    ips = [d.get("ip", "NO IP") for d in sorted_devices]
    print(f"Sorted IPs: {ips}")

    assert sorted_devices[0]["ip"] == "10.0.0.1"
    assert sorted_devices[1]["ip"] == "192.168.1.2"
    assert sorted_devices[2]["ip"] == "192.168.1.10"
    assert sorted_devices[3]["ip"] == ""
    assert "ip" not in sorted_devices[4]


################################################################################
# tests for `discover_mdns_devices`
################################################################################


def test_discover_mdns_devices_returns_list():
    """Test that discovery returns a list (may be empty in CI)"""
    devices = discover_mdns_devices(timeout=1)
    print(f"\nFound {len(devices)} mDNS devices")
    assert isinstance(devices, list)

    # If we found devices, verify structure
    for device in devices:
        print(f"Device: {device}")
        assert "name" in device
        assert "type" in device


################################################################################
# tests for `discover_ssdp_devices`
################################################################################


def test_discover_ssdp_devices_returns_list():
    """Test that discovery returns a list (may be empty in CI)"""
    devices = discover_ssdp_devices(timeout=1)
    print(f"\nFound {len(devices)} devices")
    assert isinstance(devices, list)

    # If we found devices, verify structure
    for device in devices:
        print(f"Device: {device}")
        assert "ip" in device
        assert isinstance(device["ip"], str)
