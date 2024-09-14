import logging
from unittest.mock import Mock

from bleak.backends.characteristic import BleakGATTCharacteristic
from hypothesis import given
import hypothesis.strategies as st
import pytest


from colmi_r02_client.client import Client
from colmi_r02_client import battery

MOCK_CHAR = Mock(spec=BleakGATTCharacteristic)


@given(st.binary().filter(lambda x: len(x) != 16))
def test_handle_tx_short_packet(raw):
    client = Client("unused")

    with pytest.raises(AssertionError, match="Packet is the wrong length"):
        client._handle_tx(MOCK_CHAR, bytearray(raw))


@given(st.binary(min_size=16, max_size=16).filter(lambda x: x[0] >= 127))
def test_handle_tx_error_bit(raw):
    client = Client("unused")

    with pytest.raises(AssertionError, match="Packet has error bit"):
        client._handle_tx(MOCK_CHAR, bytearray(raw))


async def test_handle_tx_real_packet():
    client = Client("unused")
    packet = bytearray(b"\x03@\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00C")
    expected = battery.BatteryInfo(64, False)

    client._handle_tx(MOCK_CHAR, packet)

    result = await client.queues[battery.CMD_BATTERY].get()
    assert result == expected


def test_handle_tx_none_parse(caplog):
    caplog.set_level(logging.DEBUG)
    client = Client("unused")
    # set time packet response is ignored
    packet = bytearray(b'\x01\x00\x01\x00"\x00\x00\x00\x00\x01\x000\x01\x00\x10f')

    client._handle_tx(MOCK_CHAR, packet)

    assert "No result returned from parser for 1" in caplog.text


def test_handle_tx_unexpected_packet(caplog):
    client = Client("unused")

    # 125 is currently unused
    packet = bytearray(b"}\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00}")

    client._handle_tx(MOCK_CHAR, packet)

    assert "Did not expect this packet:" in caplog.text
