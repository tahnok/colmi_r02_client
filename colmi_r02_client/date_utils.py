from datetime import datetime, timedelta, timezone
from typing import Iterator


def start_of_day(ts: datetime) -> datetime:
    return ts.replace(hour=0, minute=0, second=0, microsecond=0)


def end_of_day(ts: datetime) -> datetime:
    return start_of_day(ts) + timedelta(days=1, microseconds=-1)


def dates_between(start: datetime, end: datetime) -> Iterator[datetime]:
    """generator for all days between start and end. totally ignores the hours, minutes, seconds and timezones"""
    td: timedelta = end - start
    if td.days < 0:
        raise ValueError("start is after end")
    for i in range(td.days + 1):
        d = start + timedelta(days=i)
        yield d


def now() -> datetime:
    return datetime.now(tz=timezone.utc)


def minutes_so_far(dt: datetime) -> int:
    """
    Return the number of minutes elapsed in the day so far plus 1.

    I don't know why it's off by one, it just is.
    """
    midnight = datetime(dt.year, dt.month, dt.day, tzinfo=dt.tzinfo).timestamp()
    delta = dt.timestamp() - midnight  # seconds since midnight

    return round(delta / 60) + 1


def is_today(ts: datetime) -> bool:
    n = now()
    return bool(ts.year == n.year and ts.month == n.month and ts.day == n.day)
