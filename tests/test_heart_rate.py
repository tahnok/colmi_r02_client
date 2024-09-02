from datetime import datetime, timezone

from freezegun import freeze_time

from colmi_r02_client.heart_rate import (
    HeartRateLogParser,
    HeartRateLog,
    NoData,
    _minutes_so_far,
)

HEART_RATE_PACKETS = [
    bytearray(b"\x15\x00\x18\x05\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x002"),
    bytearray(b"\x15\x01\x80\xad\xb6f\x00\x00\x00\x00\x00\x00\x00\x00\x00_"),
    bytearray(b"\x15\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x17"),
    bytearray(b"\x15\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x18"),
    bytearray(b"\x15\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x19"),
    bytearray(b"\x15\x05\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1a"),
    bytearray(b"\x15\x06\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1b"),
    bytearray(b"\x15\x07\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1c"),
    bytearray(b"\x15\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1d"),
    bytearray(b"\x15\t\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1e"),
    bytearray(b"\x15\n\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1f"),
    bytearray(b"\x15\x0b\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00 "),
    bytearray(b"\x15\x0c\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00!"),
    bytearray(b'\x15\r\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"'),
    bytearray(b"\x15\x0e\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00#"),
    bytearray(b"\x15\x0f\x00\x00Y\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00}"),
    bytearray(b"\x15\x10\x00k\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x90"),
    bytearray(b"\x15\x11`\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00k\xf1"),
    bytearray(b"\x15\x12\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'"),
    bytearray(b"\x15\x13\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00P\x00\x00x"),
    bytearray(b"\x15\x14\x00\x00\x00\x00\x00\x00\x00\x00\x00F\x00\x00\x00o"),
    bytearray(b"\x15\x15\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00*"),
    bytearray(b"\x15\x16\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00+"),
    bytearray(b"\x15\x17\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00,"),
]


def test_parse_return_none_until_end():
    parser = HeartRateLogParser()
    for p in HEART_RATE_PACKETS[:-1]:
        assert parser.parse(p) is None


def test_parse_until_end():
    parser = HeartRateLogParser()
    for p in HEART_RATE_PACKETS[:-1]:
        parser.parse(p)

    result = parser.parse(HEART_RATE_PACKETS[-1])

    assert isinstance(result, HeartRateLog)

    assert len(result.heart_rates) == 288

    expected_timestamp = datetime(
        year=2024,
        month=8,
        day=10,
        hour=0,
        minute=0,
        tzinfo=timezone.utc,
    )
    assert result.timestamp == expected_timestamp


def test_parse_no_data():
    parser = HeartRateLogParser()
    result = parser.parse(
        bytearray(b"\x15\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x14"),
    )
    assert isinstance(result, NoData)


@freeze_time("2024-01-01")
def test_is_today_today():
    parser = HeartRateLogParser()
    parser._raw_heart_rates = [1] * 288
    parser.timestamp = datetime(2024, 1, 1, 1, 1, 0)

    assert parser.is_today()


@freeze_time("2024-01-02")
def test_is_today_not_today():
    parser = HeartRateLogParser()
    parser._raw_heart_rates = [1] * 288
    parser.timestamp = datetime(2024, 1, 1, 1, 1, 0)

    assert not parser.is_today()


def test_heart_rates_less_288():
    """Test that we pad the heart rate array to 288 with 0s if the raw data is less than 288 bytes long."""

    parser = HeartRateLogParser()
    parser._raw_heart_rates = [1] * 286

    hr = parser.heart_rates

    assert len(hr) == 288
    assert hr == (([1] * 286) + [0, 0])


def test_get_heart_rate_more_288():
    parser = HeartRateLogParser()
    parser._raw_heart_rates = [1] * 289

    hr = parser.heart_rates

    assert len(hr) == 288
    assert hr == ([1] * 288)


def test_get_heart_rate_288_not_today():
    parser = HeartRateLogParser()
    parser._raw_heart_rates = [1] * 288
    parser.timestamp = datetime(2020, 1, 1, 1, 1, 0)

    hr = parser.heart_rates

    assert len(hr) == 288
    assert hr == ([1] * 288)


@freeze_time("2024-01-01 01:00")
def test_get_heart_rate_288_today():
    parser = HeartRateLogParser()
    parser._raw_heart_rates = [1] * 288
    parser.timestamp = datetime(2024, 1, 1, 1, 1, 0)

    hr = parser.heart_rates

    assert len(hr) == 288
    assert hr == ([1] * 12) + ([0] * 276)


def test_minutes_so_far_midnight():
    x = datetime(2024, 1, 1)
    assert _minutes_so_far(x) == 1


def test_minutes_so_far_minutes():
    x = datetime(2024, 1, 1, 0, 15)
    assert _minutes_so_far(x) == 16


def test_minutes_so_far_day():
    x = datetime(2024, 1, 1, 23, 59)
    assert _minutes_so_far(x) == 1440


def test_with_times():
    h = HeartRateLog([60] * 288, datetime(2024, 1, 1, 5), 0, 0, 5)

    hr_with_ts = h.heart_rates_with_times()

    assert len(hr_with_ts) == 288
    assert hr_with_ts[0][1] == datetime(2024, 1, 1, 0, 0)
    assert hr_with_ts[-1][1] == datetime(2024, 1, 1, 23, 55)
