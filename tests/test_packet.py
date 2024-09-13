import pytest

from hypothesis import given
import hypothesis.strategies as st

from colmi_r02_client.packet import make_packet, checksum


@given(command=st.integers(min_value=0, max_value=255), sub_data=st.binary(max_size=14))
def test_make_packet_works_on_valid_data(command, sub_data):
    packet = make_packet(command, bytearray(sub_data))

    assert len(packet) == 16
    assert packet[-1] == checksum(packet[0:15])


@given(command=st.integers().filter(lambda x: x < 0 or x > 256))
def test_make_packet_raises_on_bad_command(command):
    with pytest.raises(AssertionError):
        make_packet(command)


@given(st.binary(min_size=15))
def test_make_packet_raises_on_too_long_sub_data(sub_data):
    with pytest.raises(AssertionError):
        make_packet(1, bytearray(sub_data))


@given(st.binary(min_size=1, max_size=14))
def test_make_packet_includes_sub_data(sub_data):
    s = bytearray(sub_data)

    p = make_packet(1, s)

    assert p[1 : 1 + len(s)] == s


def test_sample_checksum():
    message = bytearray(b"\x15\x00\x18\x05\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00")
    assert checksum(message) == 0x32


@given(st.binary())
def test_checksum(message):
    assert 0 <= checksum(bytearray(message)) < 256
