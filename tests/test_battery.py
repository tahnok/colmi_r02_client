from colmi_r02_client.battery import parse_battery, BatteryInfo


def test_parse_battery():
    resp = bytearray(b"\x03@\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00C")
    expected = BatteryInfo(battery_level=64, charging=False)

    result = parse_battery(resp)

    assert result == expected
