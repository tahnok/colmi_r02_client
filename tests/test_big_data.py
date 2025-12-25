import pytest
from colmi_r02_client.big_data import parse_bigdata_sleep_response, SleepDay, SleepPeriod

def test_parse_bigdata_sleep_response_simple():
    # Example packet for 1 day, 2 periods
    # CMD_BIG_DATA, BIG_DATA_SLEEP, dataLen(2), crc16(2), sleepDays(1), daysAgo(0), curDayBytes(8), sleepStart(60), sleepEnd(420), period1(type=2, min=30), period2(type=3, min=60)
    packet = bytearray([
        188, 39, 8, 0, 255, 255, 1,  # header
        0, 8, 60, 0, 164, 1, 2, 30, 3, 60
    ])
    days = parse_bigdata_sleep_response(packet)
    assert isinstance(days, list)
    assert len(days) == 1
    day = days[0]
    assert isinstance(day, SleepDay)
    assert day.daysAgo == 0
    assert day.sleepStart == 60
    assert day.sleepEnd == 420
    assert len(day.periods) == 2
    assert day.periods[0] == SleepPeriod(type=2, minutes=30)
    assert day.periods[1] == SleepPeriod(type=3, minutes=60)


def test_parse_bigdata_sleep_response():
    packet = bytearray(b"\xbc\'3\x00\xd4\x89\x01\x000?\x05\x1e\x02\x026\x03\x11\x05\x11\x020\x03\x10\x02 \x04 \x03 \x02 \x04\x10\x03 \x02 \x04\x10\x02 \x03 \x02@\x03 \x020\x03\x10\x02\x02\x05\x0c\x02\x19")
    days = parse_bigdata_sleep_response(packet)
    assert isinstance(days, list)
    assert len(days) == 1
    expected = SleepDay(
        daysAgo=0,
        sleepStart=1343,
        sleepEnd=542,
        periods=[
            SleepPeriod(type=2, minutes=54),
            SleepPeriod(type=3, minutes=17),
            SleepPeriod(type=5, minutes=17),
            SleepPeriod(type=2, minutes=48),
            SleepPeriod(type=3, minutes=16),
            SleepPeriod(type=2, minutes=32),
            SleepPeriod(type=4, minutes=32),
            SleepPeriod(type=3, minutes=32),
            SleepPeriod(type=2, minutes=32),
            SleepPeriod(type=4, minutes=16),
            SleepPeriod(type=3, minutes=32),
            SleepPeriod(type=2, minutes=32),
            SleepPeriod(type=4, minutes=16),
            SleepPeriod(type=2, minutes=32),
            SleepPeriod(type=3, minutes=32),
            SleepPeriod(type=2, minutes=64),
            SleepPeriod(type=3, minutes=32),
            SleepPeriod(type=2, minutes=48),
            SleepPeriod(type=3, minutes=16),
            SleepPeriod(type=2, minutes=2),
            SleepPeriod(type=5, minutes=12),
            SleepPeriod(type=2, minutes=25),
        ]
    )
    assert days[0] == expected