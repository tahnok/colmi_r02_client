from colmi_r02_client.real_time_hr import parse_heart_rate, Reading, ReadingError


def test_parse_heart_rate_hr_success():
    packet = bytearray(b"i\x01\x00N\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xb8")
    expected = Reading(1, 78)

    result = parse_heart_rate(packet)

    assert result == expected


def test_parse_heart_rate_hr_fail():
    packet = bytearray(b"i\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00k")
    expected = ReadingError(1, 1)

    result = parse_heart_rate(packet)

    assert result == expected
