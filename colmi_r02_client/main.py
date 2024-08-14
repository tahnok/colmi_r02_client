"""
A python client for connecting to the Colmi R02 Smart ring


TODO:
    - get "Stress"
    - make nicer methods for getting data from callback
    - "scan" mode instead of hard coded address
"""

import asyncio


ADDRESS = "70:CB:0D:D0:34:1C"

from colmi_r02_client.client import Client

async def main():
    print("Connecting...")

    async with Client(ADDRESS) as client:
        print("Connected")
        print("device info", await client.get_device_info())
        print("battery:", await client.get_battery())

        #target = datetime(2024,8,10,0,0,0,0,tzinfo=timezone.utc)
        #await send_packet(client, rx_char, read_heart_rate_packet(target))

def run():
    asyncio.run(main())

if __name__ == '__main__':
    run()


