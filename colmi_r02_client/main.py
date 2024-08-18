"""
A python client for connecting to the Colmi R02 Smart ring


TODO:
    - get "Stress"
    - "scan" mode instead of hard coded address
"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import logging
import time

import asyncclick as click

from colmi_r02_client.client import Client

ADDRESS = "70:CB:0D:D0:34:1C"

logging.basicConfig(level=logging.WARNING, format="%(name)s: %(message)s")

@dataclass
class CliConfig:
    record: bool = False

def from_context(context: click.Context) -> CliConfig:
    context.ensure_object(CliConfig)
    config: CliConfig = context.obj
    return config

@click.group()
@click.option("--debug/--no-debug", default=False)
@click.option("--record/--no-record", default=False, help="Write all received packets to a file")
@click.pass_context
def main(context: click.Context, debug: bool, record: bool):
    from_context(context).record = record

    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.getLogger("bleak").setLevel(logging.INFO)


@main.command()
async def info():
    """Get device info and battery level"""
    async with Client(ADDRESS) as client:
        print("device info", await client.get_device_info())
        print("battery:", await client.get_battery())

        # target = datetime(2024,8,10,0,0,0,0,tzinfo=timezone.utc)
        # await send_packet(client, rx_char, read_heart_rate_packet(target))


@main.command()
@click.option(
    "--target", type=click.DateTime(), required=True, help="The date you want logs for"
)
@click.pass_context
async def get_heart_rate_log(context: click.Context, target: datetime):
    """Get heart rate for given date (defaults to today)"""
    config = from_context(context)
    record_to = None
    if config.record:
        now = int(time.time())
        record_to = Path(f"colmi_response_capture_{now}.bin")

    async with Client(ADDRESS, record_to=record_to) as client:
        print("Data:", await client.get_heart_rate_log(target))


if __name__ == "__main__":
    main(_anyio_backend="asyncio")
