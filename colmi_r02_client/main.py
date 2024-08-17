"""
A python client for connecting to the Colmi R02 Smart ring


TODO:
    - get "Stress"
    - "scan" mode instead of hard coded address
"""

import logging

import asyncclick as click

from colmi_r02_client.client import Client

ADDRESS = "70:CB:0D:D0:34:1C"

logging.basicConfig(level=logging.WARNING, format="%(name)s: %(message)s")


@click.group()
@click.option("--debug/--no-debug", default=False)
def main(debug):
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
async def get_heart_rate_log(target):
    """Get heart rate for given date (defaults to today)"""

    async with Client(ADDRESS) as client:
        print("Data:", await client.get_heart_rate_log(target))


if __name__ == "__main__":
    main(_anyio_backend="asyncio")
