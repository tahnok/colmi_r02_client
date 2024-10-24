import asyncio
import logging
from datetime import datetime
from pathlib import Path

from bleak import BleakScanner

from colmi_r02_client.client import Client

logging.basicConfig(level=logging.INFO, format="%(name)s: %(message)s")
logger = logging.getLogger(__name__)

DEVICE_NAME_PREFIXES = [
    "R01", "R02", "R03", "R04", "R05", "R06", "R07", "R10",
    "VK-5098", "MERLIN", "Hello Ring", "RING1", "boAtring",
    "TR-R02", "SE", "EVOLVEO", "GL-SR2", "Blaupunkt", "KSIX RING",
]

async def main(address=None, name=None, output_file='hr_spo2_log.csv'):
    # Find device if address or name not provided
    if (address is None and name is None):
        devices = await BleakScanner.discover()
        for d in devices:
            dev_name = d.name
            if dev_name and any(dev_name.startswith(p) for p in DEVICE_NAME_PREFIXES):
                address = d.address
                print(f"Found device: {dev_name} at address {address}")
                break
        if address is None:
            print("No device found. Try moving the ring closer to the computer")
            return
    elif name is not None and address is None:
        devices = await BleakScanner.discover()
        found = next((x for x in devices if x.name == name), None)
        if found is None:
            print(f"No device found with name {name}")
            return
        address = found.address

    client = Client(address)
    output_path = Path(output_file)
    if not output_path.exists():
        with output_path.open('w') as f:
            f.write("timestamp,heart_rate,spo2\n")

    while True:
        try:
            if not client.bleak_client.is_connected:
                print(f"Connecting to {address}...")
                await client.connect()
                print("Connected!")

            timestamp = datetime.now().isoformat()
            print(f"{timestamp} - Getting heart rate...")
            hr_result = await client.get_realtime_heart_rate()
            hr_value = sum(hr_result) / len(hr_result) if hr_result else None
            print(f"Heart Rate: {hr_value}" if hr_value else "No heart rate data")

            print(f"{timestamp} - Getting SPO2...")
            spo2_result = await client.get_realtime_spo2()
            spo2_value = sum(spo2_result) / len(spo2_result) if spo2_result else None
            print(f"SPO2: {spo2_value}" if spo2_value else "No SPO2 data")

            with output_path.open('a') as f:
                f.write(f"{timestamp},{hr_value},{spo2_value}\n")

            await asyncio.sleep(10)  # Adjust as needed

        except Exception as e:
            print(f"Exception occurred: {e}")
            print("Attempting to disconnect and reconnect...")
            try:
                await client.disconnect()
            except Exception as disconnect_exception:
                print(f"Exception during disconnect: {disconnect_exception}")
            print("Retrying in 5 seconds...")
            await asyncio.sleep(5)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Poll heart rate and SPO2 from Colmi R02 ring")
    parser.add_argument('--address', help='Bluetooth address of the device')
    parser.add_argument('--name', help='Bluetooth name of the device')
    parser.add_argument('--output', help='Output CSV file', default='hr_spo2_log.csv')
    args = parser.parse_args()

    asyncio.run(main(address=args.address, name=args.name, output_file=args.output))

