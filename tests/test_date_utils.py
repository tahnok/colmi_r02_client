from datetime import datetime, timedelta, timezone

from freezegun import freeze_time
from hypothesis import given, strategies as st
import pytest

from colmi_r02_client.date_utils import start_of_day, end_of_day, minutes_so_far, is_today, dates_between


@given(st.datetimes(timezones=st.timezones()))
def test_start_of_day(ts: datetime):
    x = start_of_day(ts)
    assert x.hour == 0
    assert x.minute == 0
    assert x.second == 0
    assert x.microsecond == 0


@given(st.datetimes(timezones=st.timezones()))
def test_end_of_day(ts: datetime):
    x = end_of_day(ts)
    assert x.hour == 23
    assert x.minute == 59
    assert x.second == 59
    assert x.microsecond == 999999


@freeze_time("2024-01-01")
def test_is_today_today():
    d = datetime(2024, 1, 1, 1, 1, 0)

    assert is_today(d)


@freeze_time("2024-01-02")
def test_is_today_not_today():
    d = datetime(2024, 1, 1, 1, 1, 0)

    assert not is_today(d)


@given(hour=st.integers(min_value=-23, max_value=23))
def test_minutes_so_far_midnight(hour):
    tz = timezone(timedelta(hours=hour))
    x = datetime(2024, 1, 1, tzinfo=tz)
    assert minutes_so_far(x) == 1


@given(hour=st.integers(min_value=-23, max_value=23))
def test_minutes_so_far_minutes(hour):
    tz = timezone(timedelta(hours=hour))
    x = datetime(2024, 1, 1, 0, 15, tzinfo=tz)
    assert minutes_so_far(x) == 16


@given(hour=st.integers(min_value=-23, max_value=23))
def test_minutes_so_far_day(hour):
    tz = timezone(timedelta(hours=hour))
    x = datetime(2024, 1, 1, 23, 59, tzinfo=tz)
    assert minutes_so_far(x) == 1440


def test_dates_between_one():
    dt = datetime(2024, 11, 11)
    assert [dt] == list(dates_between(dt, dt))


def test_dates_between_two():
    start = datetime(2024, 11, 11)
    end = datetime(2024, 11, 12)
    assert [start, end] == list(dates_between(start, end))


def test_dates_between_many():
    start = datetime(2024, 10, 11)
    end = datetime(2024, 10, 14)
    assert [start, datetime(2024, 10, 12), datetime(2024, 10, 13), end] == list(dates_between(start, end))


def test_dates_between_end_before_start():
    start = datetime(2024, 11, 12)
    end = datetime(2024, 11, 11)
    with pytest.raises(ValueError):
        list(dates_between(start, end))
