from datetime import datetime, timezone, timedelta

from colmi_r02_client.set_time import byte_to_bcd, set_time_packet, CMD_SET_TIME, parse_set_time_packet

import pytest


@pytest.mark.parametrize(("normal", "bcd"), [(0, 0), (10, 0b00010000), (99, 0b10011001)])
def test_byte_to_bcd(normal, bcd):
    assert bcd == byte_to_bcd(normal)


@pytest.mark.parametrize("bad", [-1, 100, 1000])
def test_byte_to_bcd_bad(bad):
    with pytest.raises(AssertionError):
        byte_to_bcd(bad)


def test_set_time_packet():
    ts = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    expected = bytearray(b"\x01$\x01\x01\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00(")

    actual = set_time_packet(ts)

    assert actual == expected

    assert actual[0] == CMD_SET_TIME


def test_set_time_1999():
    ts = datetime(1999, 1, 1, 0, 0, 0)
    with pytest.raises(AssertionError):
        set_time_packet(ts)


def test_set_time_with_timezone():
    ts = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone(timedelta(hours=-4)))
    expected = bytearray(b"\x01$\x01\x01\x04\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00,")

    actual = set_time_packet(ts)

    assert actual == expected


def test_parse_set_time_response():
    packet = bytearray(b'\x01\x00\x01\x00"\x00\x00\x00\x00\x01\x000\x01\x00\x10f')

    capabilities = parse_set_time_packet(packet)

    assert capabilities["mSupportManualHeart"]
    assert not capabilities["mSupportBloodSugar"]
