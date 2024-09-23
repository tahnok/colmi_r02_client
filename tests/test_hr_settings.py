from hypothesis import given, strategies as st

from colmi_r02_client.hr_settings import parse_heart_rate_log_settings, HeartRateLogSettings, hr_log_settings_packet


def test_parse_enabled():
    resp = bytearray(b"\x16\x01\x01<\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00T")
    expected = HeartRateLogSettings(enabled=True, interval=60)

    result = parse_heart_rate_log_settings(resp)

    assert result == expected


def test_parse_disabled():
    resp = bytearray(b"\x16\x01\x02<\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00U")
    expected = HeartRateLogSettings(enabled=False, interval=60)

    result = parse_heart_rate_log_settings(resp)

    assert result == expected


@given(st.booleans(), st.integers(min_value=1, max_value=255))
def test_hr_settings_packet(enabled, interval):
    packet = hr_log_settings_packet(HeartRateLogSettings(enabled, interval))
    assert len(packet) == 16
