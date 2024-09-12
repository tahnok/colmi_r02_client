from unittest.mock import Mock
import pytest

from bleak.backends.characteristic import BleakGATTCharacteristic

from colmi_r02_client.client import Client

MOCK_CHAR = Mock(spec=BleakGATTCharacteristic)


def test_handle_tx_short_packet():
    client = Client("unused")

    with pytest.raises(AssertionError, match="Packet is the wrong length"):
        client._handle_tx(MOCK_CHAR, bytearray())


def test_handle_tx_error_bit():
    client = Client("unused")

    with pytest.raises(AssertionError, match="Packet has error bit"):
        client._handle_tx(MOCK_CHAR, bytearray(b"\xf1" * 16))
