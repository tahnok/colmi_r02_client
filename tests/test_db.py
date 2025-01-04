from datetime import datetime, timezone
import os
from pathlib import Path
from unittest.mock import create_autospec

from hypothesis import given, strategies as st
import pytest
from sqlalchemy import text, select, func, Dialect
from sqlalchemy.exc import IntegrityError

from colmi_r02_client.client import FullData
from colmi_r02_client import hr, steps
from colmi_r02_client.db import (
    get_db_session,
    create_or_find_ring,
    full_sync,
    Ring,
    HeartRate,
    SportDetail,
    Sync,
    get_last_sync,
    DateTimeInUTC,
)


@pytest.fixture(name="address")
def get_address() -> str:
    return "fake"


@pytest.fixture(name="empty_full_data")
def get_empty_full_data(address) -> FullData:
    return FullData(address=address, heart_rates=[], sport_details=[])


def test_get_db_session_memory():
    with get_db_session() as session:
        assert session.scalars(text("SELECT 1")).one() == 1


def test_get_db_session_file(tmp_path: Path):
    db_file = tmp_path / "test.sqlite"
    assert not db_file.exists()

    with get_db_session(db_file) as session:
        assert session.scalars(text("SELECT 1")).one() == 1

    assert db_file.exists()


def test_get_db_tables_exist():
    with get_db_session() as session:
        tables = set(session.scalars(text("SELECT name FROM sqlite_master WHERE type ='table'")).fetchall())
        assert tables == {
            "rings",
            "syncs",
            "heart_rates",
            "sport_details",
        }


def test_get_db_schema():
    """
    I want to have each table schema in a spot that's
    easy to update but also see. Maybe in a .sql file?
    """
    schema_path = Path("tests/database_schema.sql")
    expected = schema_path.read_text()
    with get_db_session() as session:
        actual = "\n\n".join(session.scalars(text("SELECT sql FROM sqlite_schema where type = 'table'")).fetchall())
    if actual != expected:
        if os.getenv("UPDATE_SCHEMA", None):
            schema_path.write_text(actual)
            pytest.fail("Test failed because we rewrote the schema file")
        else:
            assert actual == expected, "Schema mismatch, if this is expected rerun with UPDATE_SCHEMA=1"


def test_create_new_ring():
    with get_db_session() as session:
        address = "address"
        ring = create_or_find_ring(session, address)
        assert ring.address == address


def test_fetch_old_ring():
    with get_db_session() as session:
        address = "address"
        new_ring = create_or_find_ring(session, address)
        old_ring = create_or_find_ring(session, address)
        assert old_ring == new_ring
        assert old_ring.address == address


def test_ring_sync_id_required_for_heart_rate():
    with get_db_session() as session, pytest.raises(IntegrityError):
        session.add(HeartRate(reading=1, timestamp=datetime(2024, 1, 1, tzinfo=timezone.utc), ring_id=None, sync_id=None))
        session.commit()


def test_sync_creates_ring(address, empty_full_data):
    with get_db_session() as session:
        full_sync(session, empty_full_data)

    ring = session.scalars(select(Ring)).one()
    assert address == ring.address


def test_sync_uses_existing_ring(address, empty_full_data):
    with get_db_session() as session:
        create_or_find_ring(session, address)
        full_sync(session, empty_full_data)

        assert session.scalars(func.count(Ring.ring_id)).one() == 1


def test_sync_creates_sync(address, empty_full_data):
    with get_db_session() as session:
        full_sync(session, empty_full_data)

        sync_obj = session.scalars(select(Sync)).one()

        assert sync_obj.ring.address == address


def test_sync_writes_heart_rates():
    address = "fake"
    hrl = hr.HeartRateLog(
        heart_rates=[80] * 288,
        timestamp=datetime(2024, 11, 11, 11, 11, tzinfo=timezone.utc),
        size=24,
        index=295,
        range=5,
    )
    fd = FullData(address=address, heart_rates=[hrl], sport_details=[])
    with get_db_session() as session:
        full_sync(session, fd)

        ring = session.scalars(select(Ring)).one()
        logs = session.scalars(select(HeartRate)).all()
        sync_obj = session.scalars(select(Sync)).one()

    assert len(logs) == 288
    assert logs[0].ring_id == ring.ring_id
    assert logs[0].reading == 80
    assert logs[0].timestamp == datetime(2024, 11, 11, 0, 0, tzinfo=timezone.utc)
    assert logs[1].timestamp == datetime(2024, 11, 11, 0, 5, tzinfo=timezone.utc)
    assert logs[0].sync_id == sync_obj.sync_id


def test_sync_writes_heart_rates_only_non_zero_heart_rates():
    address = "fake"
    hrl = hr.HeartRateLog(
        heart_rates=[80] * 8 + [0] * 280,
        timestamp=datetime(2024, 11, 11, 11, 11, tzinfo=timezone.utc),
        size=24,
        index=295,
        range=5,
    )
    fd = FullData(address=address, heart_rates=[hrl], sport_details=[])
    with get_db_session() as session:
        full_sync(session, fd)

        logs = session.scalars(select(HeartRate)).all()

    assert len(logs) == 8


def test_sync_writes_heart_rates_once():
    address = "fake"
    hrl_1 = hr.HeartRateLog(
        heart_rates=[80] * 8 + [0] * 280,
        timestamp=datetime(2024, 11, 11, 11, 11, tzinfo=timezone.utc),
        size=24,
        index=295,
        range=5,
    )
    fd_1 = FullData(address=address, heart_rates=[hrl_1], sport_details=[])

    hrl_2 = hr.HeartRateLog(
        heart_rates=[80] * 288,
        timestamp=datetime(2024, 11, 11, 11, 11, tzinfo=timezone.utc),
        size=24,
        index=295,
        range=5,
    )
    fd_2 = FullData(address=address, heart_rates=[hrl_2], sport_details=[])
    with get_db_session() as session:
        full_sync(session, fd_1)
        full_sync(session, fd_2)

        logs = session.scalars(select(HeartRate)).all()

    assert len(logs) == 288


def test_sync_handles_inconsistent_data(caplog):
    address = "fake"
    hrl_1 = hr.HeartRateLog(
        heart_rates=[80] * 288,
        timestamp=datetime(2024, 11, 11, 11, 11, tzinfo=timezone.utc),
        size=24,
        index=295,
        range=5,
    )
    fd_1 = FullData(address=address, heart_rates=[hrl_1], sport_details=[])

    hrl_2 = hr.HeartRateLog(
        heart_rates=[90] * 288,
        timestamp=datetime(2024, 11, 11, 11, 11, tzinfo=timezone.utc),
        size=24,
        index=295,
        range=5,
    )
    fd_2 = FullData(address=address, heart_rates=[hrl_2], sport_details=[])
    with get_db_session() as session:
        full_sync(session, fd_1)
        full_sync(session, fd_2)

        logs = session.scalars(select(HeartRate)).all()

    assert len(logs) == 288
    assert all(log.reading == 80 for log in logs)
    assert "Inconsistent data detected! 2024-11-11 00:00:00+00:00 is 80 in db but got 90 from ring" in caplog.text


def test_full_sync_writes_sport_details():
    address = "fake"
    sd = steps.SportDetail(
        year=2025,
        month=1,
        day=1,
        time_index=0,
        calories=4200,
        steps=6969,
        distance=1234,
    )
    fd = FullData(address=address, heart_rates=[], sport_details=[[sd]])
    with get_db_session() as session:
        full_sync(session, fd)

        ring = session.scalars(select(Ring)).one()
        sport_details = session.scalars(select(SportDetail)).all()
        sync_obj = session.scalars(select(Sync)).one()

    assert len(sport_details) == 1
    assert sport_details[0].ring_id == ring.ring_id
    assert sport_details[0].timestamp == datetime(2025, 1, 1, 0, 0, tzinfo=timezone.utc)
    assert sport_details[0].sync_id == sync_obj.sync_id


def test_full_sync_no_sport_details():
    address = "fake"
    fd = FullData(address=address, heart_rates=[], sport_details=[steps.NoData(), steps.NoData()])
    with get_db_session() as session:
        full_sync(session, fd)

        sport_details = session.scalars(select(SportDetail)).all()

    assert len(sport_details) == 0


def test_get_last_sync_never():
    with get_db_session() as session:
        assert get_last_sync(session) is None


def test_get_sync_once():
    with get_db_session() as session:
        ring = Ring(address="foo")
        timestamp = datetime(2024, 11, 11, 11, tzinfo=timezone.utc)
        session.add(Sync(ring=ring, timestamp=timestamp))
        session.commit()
        assert get_last_sync(session) == timestamp


def test_get_sync_many():
    with get_db_session() as session:
        ring = Ring(address="foo")
        first = datetime(2024, 11, 11, 11, tzinfo=timezone.utc)
        second = datetime(2024, 12, 12, 12, tzinfo=timezone.utc)
        session.add(Sync(ring=ring, timestamp=first))
        session.add(Sync(ring=ring, timestamp=second))
        session.commit()
        assert get_last_sync(session) == second


def test_datetimes_have_timezones():
    with get_db_session() as session:
        ring = Ring(address="foo")
        timestamp = datetime(2024, 11, 11, 11, tzinfo=timezone.utc)
        session.add(Sync(ring=ring, timestamp=timestamp))
        session.commit()
        assert get_last_sync(session) == timestamp
        assert timestamp.tzinfo is not None


def test_datetime_in_utc_process_bind_none():
    dtiu = DateTimeInUTC()
    dialect = create_autospec(Dialect)

    assert dtiu.process_bind_param(None, dialect) is None


@pytest.mark.skip
@given(st.datetimes())
def test_datetime_in_utc_process_bind_no_tz(ts: datetime):
    dtiu = DateTimeInUTC()
    dialect = create_autospec(Dialect)

    with pytest.raises(ValueError):
        dtiu.process_bind_param(ts, dialect)


@pytest.mark.skip
@given(st.datetimes(timezones=st.timezones()))
def test_datetime_in_utc_process_bind_tz(ts: datetime):
    dtiu = DateTimeInUTC()
    dialect = create_autospec(Dialect)

    result = dtiu.process_bind_param(ts, dialect)

    assert result is not None
    assert result.tzinfo == timezone.utc
    assert ts.astimezone(timezone.utc) == result


def test_datetime_in_utc_process_result_none():
    dtiu = DateTimeInUTC()
    dialect = create_autospec(Dialect)

    assert dtiu.process_result_value(None, dialect) is None


@pytest.mark.skip
@given(st.datetimes())
def test_datetime_in_utc_process_result_no_tz(ts: datetime):
    dtiu = DateTimeInUTC()
    dialect = create_autospec(Dialect)

    result = dtiu.process_result_value(ts, dialect)

    assert result is not None
    assert result.tzinfo == timezone.utc


@pytest.mark.skip
@given(st.datetimes(timezones=st.timezones()))
def test_datetime_in_utc_process_tz(ts: datetime):
    dtiu = DateTimeInUTC()
    dialect = create_autospec(Dialect)

    result = dtiu.process_result_value(ts, dialect)

    assert result is not None
    assert result.tzinfo == timezone.utc
    assert ts.astimezone(timezone.utc) == result
