from datetime import datetime, timezone

from colmi_r02_client.steps import SportDetailParser, SportDetail, NoData


def test_parse_simple():
    sdp = SportDetailParser()

    r = sdp.parse(bytearray(b"C\xf0\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x005"))

    assert r is None
    r = sdp.parse(bytearray(b"C$\x10\x15\\\x00\x01y\x00\x15\x00\x10\x00\x00\x00\x87"))

    assert r == [SportDetail(year=2024, month=10, day=15, time_index=92, calories=1210, steps=21, distance=16)]


def test_parse_multi():
    packets = [
        bytearray(b"C\xf0\x05\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x009"),
        bytearray(b"C#\x08\x13\x10\x00\x05\xc8\x000\x00\x1b\x00\x00\x00\xa9"),
        bytearray(b"C#\x08\x13\x14\x01\x05\xb6\x18\xaa\x04i\x03\x00\x00\x83"),
        bytearray(b"C#\x08\x13\x18\x02\x058\x04\xe1\x00\x95\x00\x00\x00R"),
        bytearray(b"C#\x08\x13\x1c\x03\x05\x05\x02l\x00H\x00\x00\x00`"),
        bytearray(b"C#\x08\x13L\x04\x05\xef\x01c\x00D\x00\x00\x00m"),
    ]
    expected = [
        SportDetail(
            year=2023,
            month=8,
            day=13,
            time_index=16,
            calories=2000,
            steps=48,
            distance=27,
        ),
        SportDetail(
            year=2023,
            month=8,
            day=13,
            time_index=20,
            calories=63260,
            steps=1194,
            distance=873,
        ),
        SportDetail(
            year=2023,
            month=8,
            day=13,
            time_index=24,
            calories=10800,
            steps=225,
            distance=149,
        ),
        SportDetail(
            year=2023,
            month=8,
            day=13,
            time_index=28,
            calories=5170,
            steps=108,
            distance=72,
        ),
        SportDetail(
            year=2023,
            month=8,
            day=13,
            time_index=76,
            calories=4950,
            steps=99,
            distance=68,
        ),
    ]

    sdp = SportDetailParser()
    for p in packets[:-1]:
        x = sdp.parse(p)
        assert x is None, f"Unexpected return from {p}"

    actual = sdp.parse(packets[-1])

    assert actual == expected


def test_no_data_parse():
    resp = bytearray(b"C\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00B")
    sdp = SportDetailParser()

    actual = sdp.parse(resp)

    assert isinstance(actual, NoData)


def test_timestamp_midnight():
    sd = SportDetail(
        year=2025,
        month=1,
        day=1,
        time_index=0,
        calories=0,
        distance=0,
        steps=0,
    )
    ts = datetime(2025, 1, 1, 0, 0, tzinfo=timezone.utc)
    assert sd.timestamp == ts


def test_timestamp_one_more():
    sd = SportDetail(
        year=2025,
        month=1,
        day=1,
        time_index=95,
        calories=0,
        distance=0,
        steps=0,
    )
    ts = datetime(2025, 1, 1, 23, 45, tzinfo=timezone.utc)
    assert sd.timestamp == ts
