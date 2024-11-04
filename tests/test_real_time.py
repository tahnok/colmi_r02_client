import pytest
from colmi_r02_client.real_time import enum, packet


@pytest.mark.parametrize("reading_type", enum.RealTimeReading)
def test_packet_generation(reading_type: enum.RealTimeReading):
    result = packet.get_start_packet(reading_type)

    assert result[0] == packet.CMD_START_REAL_TIME
    assert result[1] == reading_type
    assert result[2] == enum.Action.START
    assert result[-1] == packet.CMD_START_REAL_TIME + enum.Action.START + reading_type

    result = packet.get_continue_packet(reading_type)

    assert result[0] == packet.CMD_START_REAL_TIME
    assert result[1] == reading_type
    assert result[2] == enum.Action.CONTINUE
    assert result[-1] == packet.CMD_START_REAL_TIME + enum.Action.CONTINUE + reading_type

    result = packet.get_stop_packet(reading_type)

    assert result[0] == packet.CMD_STOP_REAL_TIME
    assert result[1] == reading_type
    assert result[2] == result[3] == 0
    assert result[-1] == packet.CMD_STOP_REAL_TIME + reading_type


def test_parse_real_time_reading_success():
    input = bytearray(b"i\x01\x00N\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xb8")
    expected = packet.Reading(1, 78)

    result = packet.parse_real_time_reading(input)

    assert result == expected


def test_parse_real_time_reading_fail():
    input = bytearray(b"i\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00k")
    expected = packet.ReadingError(1, 1)

    result = packet.parse_real_time_reading(input)

    assert result == expected
