import pytest
from colmi_r02_client import real_time


@pytest.mark.parametrize("reading_type", real_time.RealTimeReading)
def test_real_time_generation(reading_type: real_time.RealTimeReading):
    result = real_time.get_start_packet(reading_type)

    assert result[0] == real_time.CMD_START_REAL_TIME
    assert result[1] == reading_type
    assert result[2] == real_time.Action.START
    assert result[-1] == real_time.CMD_START_REAL_TIME + real_time.Action.START + reading_type

    result = real_time.get_continue_packet(reading_type)

    assert result[0] == real_time.CMD_START_REAL_TIME
    assert result[1] == reading_type
    assert result[2] == real_time.Action.CONTINUE
    assert result[-1] == real_time.CMD_START_REAL_TIME + real_time.Action.CONTINUE + reading_type

    result = real_time.get_stop_packet(reading_type)

    assert result[0] == real_time.CMD_STOP_REAL_TIME
    assert result[1] == reading_type
    assert result[2] == result[3] == 0
    assert result[-1] == real_time.CMD_STOP_REAL_TIME + reading_type


def test_parse_real_time_reading_success():
    input = bytearray(b"i\x01\x00N\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xb8")
    expected = real_time.Reading(real_time.RealTimeReading.HEART_RATE, 78)

    result = real_time.parse_real_time_reading(input)

    assert result == expected


def test_parse_real_time_reading_fail():
    input = bytearray(b"i\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00k")
    expected = real_time.ReadingError(real_time.RealTimeReading.HEART_RATE, 1)

    result = real_time.parse_real_time_reading(input)

    assert result == expected
