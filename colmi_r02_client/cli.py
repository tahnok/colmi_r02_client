"""
A python client for connecting to the Colmi R02 Smart ring
"""

import csv
import dataclasses
from datetime import datetime, timezone, timedelta
from io import StringIO
from pathlib import Path
import logging
import time

import asyncclick as click
from bleak import BleakScanner

from colmi_r02_client.client import Client
from colmi_r02_client import steps, pretty_print, db, date_utils, hr, real_time

logging.basicConfig(level=logging.WARNING, format="%(name)s: %(message)s")

logger = logging.getLogger(__name__)


@click.group()
@click.option("--debug/--no-debug", default=False)
@click.option(
    "--record/--no-record",
    default=False,
    help="Write all received packets to a file",
)
@click.option("--address", required=False, help="Bluetooth address")
@click.option("--name", required=False, help="Bluetooth name of the device, slower but will work on macOS")
@click.pass_context
async def cli_client(context: click.Context, debug: bool, record: bool, address: str | None, name: str | None) -> None:
    if (address is None and name is None) or (address is not None and name is not None):
        context.fail("You must pass either the address option(preferred) or the name option, but not both")

    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.getLogger("bleak").setLevel(logging.INFO)

    record_to = None
    if record:
        now = int(time.time())
        captures = Path("captures")
        captures.mkdir(exist_ok=True)
        record_to = captures / Path(f"colmi_response_capture_{now}.bin")
        logger.info(f"Recording responses to {record_to}")

    if name is not None:
        devices = await BleakScanner.discover()
        found = next((x for x in devices if x.name == name), None)
        if found is None:
            context.fail("No device found with given name")
        address = found.address

    assert address

    client = Client(address, record_to=record_to)

    context.obj = client


@cli_client.command()
@click.pass_obj
async def info(client: Client) -> None:
    """Get device info and battery level"""

    async with client:
        print("device info", await client.get_device_info())
        print("battery:", await client.get_battery())


@cli_client.command()
@click.option(
    "--target",
    type=click.DateTime(),
    required=True,
    help="The date you want logs for",
)
@click.pass_obj
async def get_heart_rate_log(client: Client, target: datetime) -> None:
    """Get heart rate for given date"""

    async with client:
        log = await client.get_heart_rate_log(target)
        print("Data:", log)
        if isinstance(log, hr.HeartRateLog):
            for reading, ts in log.heart_rates_with_times():
                if reading != 0:
                    print(f"{ts.strftime('%H:%M')}, {reading}")


@cli_client.command()
@click.option(
    "--when",
    type=click.DateTime(),
    required=False,
    help="The date and time you want to set the ring to",
)
@click.pass_obj
async def set_time(client: Client, when: datetime | None) -> None:
    """
    Set the time on the ring, required if you want to be able to interpret any of the logged data
    """

    if when is None:
        when = date_utils.now()
    async with client:
        await client.set_time(when)
    click.echo("Time set successfully")
    click.echo("Please ignore the unexpected packet. It's expectedly unexpected")


@cli_client.command()
@click.pass_obj
async def get_heart_rate_log_settings(client: Client) -> None:
    """Get heart rate log settings"""

    async with client:
        click.echo("heart rate log settings:")
        click.echo(await client.get_heart_rate_log_settings())


@cli_client.command()
@click.option("--enable/--disable", default=True, show_default=True, help="Logging status")
@click.option(
    "--interval",
    type=click.IntRange(0, 255),
    help="Interval in minutes to measure heart rate",
    default=60,
    show_default=True,
)
@click.pass_obj
async def set_heart_rate_log_settings(client: Client, enable: bool, interval: int) -> None:
    """Set heart rate log settings"""

    async with client:
        click.echo("Changing heart rate log settings")
        await client.set_heart_rate_log_settings(enable, interval)
        click.echo(await client.get_heart_rate_log_settings())
        click.echo("Done")


@cli_client.command()
@click.pass_obj
@click.argument("reading", nargs=1, type=click.Choice(list(real_time.REAL_TIME_MAPPING.keys())))
async def get_real_time(client: Client, reading: str) -> None:
    """Get any real time measurement (like heart rate or SPO2)"""
    async with client:
        click.echo("Starting reading, please wait.")
        reading_type = real_time.REAL_TIME_MAPPING[reading]
        result = await client.get_realtime_reading(reading_type)
        if result:
            click.echo(result)
        else:
            click.echo(f"Error, no {reading.replace('-', ' ')} detected. Is the ring being worn?")


@cli_client.command()
@click.pass_obj
@click.option(
    "--when",
    type=click.DateTime(),
    required=False,
    help="The date you want steps for",
)
@click.option("--as-csv", is_flag=True, help="Print as CSV", default=False)
async def get_steps(client: Client, when: datetime | None = None, as_csv: bool = False) -> None:
    """Get step data"""

    if when is None:
        when = datetime.now(tz=timezone.utc)
    async with client:
        result = await client.get_steps(when)
        if isinstance(result, steps.NoData):
            click.echo("No results for day")
            return

        if not as_csv:
            click.echo(pretty_print.print_dataclasses(result))
        else:
            out = StringIO()
            writer = csv.DictWriter(out, fieldnames=[f.name for f in dataclasses.fields(steps.SportDetail)])
            writer.writeheader()
            for r in result:
                writer.writerow(dataclasses.asdict(r))
            click.echo(out.getvalue())


@cli_client.command()
@click.pass_obj
async def reboot(client: Client) -> None:
    """Reboot the ring"""

    async with client:
        await client.reboot()
        click.echo("Ring rebooted")


@cli_client.command()
@click.pass_obj
async def firehose(client: Client) -> None:
    """Start firehose data dump for 5 seconds"""

    async with client:
        await client.get_firehose()
        click.echo("Firehose completed")


@cli_client.command()
@click.pass_obj
@click.option(
    "--command",
    type=click.IntRange(min=0, max=255),
    help="Raw command",
)
@click.option(
    "--subdata",
    type=str,
    help="Hex encoded subdata array, will be parsed into a bytearray",
)
@click.option("--replies", type=click.IntRange(min=0), default=0, help="How many reply packets to wait for")
async def raw(client: Client, command: int, subdata: str | None, replies: int) -> None:
    """Send the ring a raw command"""

    p_subdata = bytearray.fromhex(subdata) if subdata is not None else bytearray()

    async with client:
        results = await client.raw(command, p_subdata, replies)
        click.echo(results)


@cli_client.command()
@click.pass_obj
@click.option(
    "--db",
    "db_path",
    type=click.Path(writable=True, path_type=Path),
    help="Path to a directory or file to use as the database. If dir, then filename will be ring_data.sqlite",
)
@click.option(
    "--start",
    type=click.DateTime(),
    required=False,
    help="The date you want to start grabbing data from",
)
@click.option(
    "--end",
    type=click.DateTime(),
    required=False,
    help="The date you want to start grabbing data to",
)
async def sync(client: Client, db_path: Path | None, start: datetime | None, end: datetime | None) -> None:
    """
    Sync all data from the ring to a sqlite database

    Currently grabs:
        - heart rates
    """

    if db_path is None:
        db_path = Path.cwd()
    if db_path.is_dir():
        db_path /= Path("ring_data.sqlite")

    click.echo(f"Writing to {db_path}")
    with db.get_db_session(db_path) as session:
        if start is None:
            start = db.get_last_sync(session, client.address)
        else:
            start = date_utils.naive_to_aware(start)

        if start is None:
            start = date_utils.now() - timedelta(days=7)

        if end is None:
            end = date_utils.now()
        else:
            end = date_utils.naive_to_aware(end)

        click.echo(f"Syncing from {start} to {end}")

        async with client:
            fd = await client.get_full_data(start, end)
            db.full_sync(session, fd)
            when = datetime.now(tz=timezone.utc)
            click.echo("Ignore unexpect packet")
            await client.set_time(when)

    click.echo("Done")


DEVICE_NAME_PREFIXES = [
    "R01",
    "R02",
    "R03",
    "R04",
    "R05",
    "R06",
    "R07",
    "R09",
    "R10",
    "COLMI",
    "VK-5098",
    "MERLIN",
    "Hello Ring",
    "RING1",
    "boAtring",
    "TR-R02",
    "SE",
    "EVOLVEO",
    "GL-SR2",
    "Blaupunkt",
    "KSIX RING",
]


@click.group()
async def util():
    """Generic utilities for the R02 that don't need an address."""


@util.command()
@click.option("--all", is_flag=True, help="Print all devices, no name filtering", default=False)
async def scan(all: bool) -> None:
    """Scan for possible devices based on known prefixes and print the bluetooth address."""

    # TODO maybe bluetooth specific stuff like this should be in another package?
    devices = await BleakScanner.discover()

    if len(devices) > 0:
        click.echo("Found device(s)")
        click.echo(f"{'Name':>20}  | Address")
        click.echo("-" * 44)
        for d in devices:
            name = d.name
            if name and (all or any(name for p in DEVICE_NAME_PREFIXES if name.startswith(p))):
                click.echo(f"{name:>20}  |  {d.address}")
    else:
        click.echo("No devices found. Try moving the ring closer to computer")
