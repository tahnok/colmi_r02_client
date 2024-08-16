import asyncio
from collections.abc import Callable
from datetime import datetime, timezone
import logging
from types import TracebackType
from typing import Any

from bleak import BleakClient
from bleak.backends.characteristic import BleakGATTCharacteristic

from colmi_r02_client import (
    battery,
    real_time_heart_rate,
    steps,
    set_time,
    blink_twice,
    heart_rate,
)

UART_SERVICE_UUID = "6E40FFF0-B5A3-F393-E0A9-E50E24DCCA9E"
UART_RX_CHAR_UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"
UART_TX_CHAR_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"

DEVICE_INFO_UUID = "0000180A-0000-1000-8000-00805F9B34FB"
DEVICE_HW_UUID = "00002A27-0000-1000-8000-00805F9B34FB"
DEVICE_FW_UUID = "00002A26-0000-1000-8000-00805F9B34FB"

logger = logging.getLogger(__name__)


def empty_parse(_packet: bytearray) -> None:
    """Used for commands that we expect a response, but there's nothing in the response"""
    return None


def log_packet(packet: bytearray) -> None:
    print("received: ", packet)


# TODO put these somewhere nice
# these are commands that we expect to have a response returned for
# they must accept a packet as bytearray and then return a value to be put
# in the queue for that command type
# NOTE: if the value returned is None, it is not added to the queue
COMMAND_HANDLERS: dict[int, Callable[[bytearray], Any]] = {
    battery.CMD_BATTERY: battery.parse_battery,
    real_time_heart_rate.CMD_START_HEART_RATE: real_time_heart_rate.parse_heart_rate,
    real_time_heart_rate.CMD_STOP_HEART_RATE: empty_parse,
    steps.CMD_GET_STEP_SOMEDAY: steps.SportDetailParser().parse,
    heart_rate.CMD_READ_HEART_RATE: heart_rate.HeartRateLogParser().parse,
}


class Client:
    def __init__(self, address: str):
        self.address = address
        self.bleak_client = BleakClient(self.address)
        self.queues = {cmd: asyncio.Queue() for cmd in COMMAND_HANDLERS.keys()}

    async def __aenter__(self) -> "Client":
        logger.info(f"Connecting to {self.address}")
        await self.connect()
        logger.info("Connected!")
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException],
        exc_val: BaseException,
        exc_tb: TracebackType,
    ) -> None:
        await self.disconnect()

    async def connect(self):
        await self.bleak_client.connect()

        nrf_uart_service = self.bleak_client.services.get_service(UART_SERVICE_UUID)
        assert nrf_uart_service
        rx_char = nrf_uart_service.get_characteristic(UART_RX_CHAR_UUID)
        assert rx_char
        self.rx_char = rx_char

        await self.bleak_client.start_notify(UART_TX_CHAR_UUID, self.handle_tx)

    async def disconnect(self):
        await self.bleak_client.disconnect()

    def handle_tx(self, _: BleakGATTCharacteristic, packet: bytearray) -> None:
        logger.info(f"Received packet {packet}")
        packet_type = packet[0]
        assert packet_type < 127, f"Packet has error bit set {packet}"

        if packet_type in COMMAND_HANDLERS:
            result = COMMAND_HANDLERS[packet_type](packet)
            if result is not None:
                self.queues[packet_type].put_nowait(result)
            else:
                logger.debug(f"No result returned from parser for {packet_type}")
        else:
            logger.warn("Did not expect this packet", packet)

    async def send_packet(self, packet: bytearray) -> None:
        await self.bleak_client.write_gatt_char(self.rx_char, packet, response=False)

    async def get_battery(self):
        await self.send_packet(battery.BATTERY_PACKET)
        return await self.queues[battery.CMD_BATTERY].get()

    async def get_realtime_heart_rate(self) -> list[int]:
        await self.send_packet(real_time_heart_rate.START_HEART_RATE_PACKET)
        print("wrote HR reading packet, waiting...")

        valid_hr: list[int] = []
        tries = 0
        while len(valid_hr) < 6 and tries < 20:
            try:
                data = await asyncio.wait_for(
                    self.queues[real_time_heart_rate.CMD_START_HEART_RATE].get(), 2
                )
                if data["error_code"] == 1:
                    print("No heart rate detected, probably not on")
                    break
                if data["value"] != 0:
                    valid_hr.append(data["value"])
            except TimeoutError:
                print(".")
                tries += 1
                await self.send_packet(real_time_heart_rate.CONTINUE_HEART_RATE_PACKET)

        await self.send_packet(
            real_time_heart_rate.STOP_HEART_RATE_PACKET,
        )
        return valid_hr

    async def get_realtime_spo2(self) -> list[int]:
        await self.send_packet(real_time_heart_rate.START_SPO2_PACKET)
        print("wrote SPO2 reading packet, waiting...")

        valid_spo2: list[int] = []
        tries = 0
        while len(valid_spo2) < 6 and tries < 20:
            try:
                data = await asyncio.wait_for(
                    self.queues[real_time_heart_rate.CMD_START_HEART_RATE].get(), 2
                )
                if data["error_code"] == 1:
                    print("No heart rate detected, probably not on")
                    break
                if data["value"] != 0:
                    valid_spo2.append(data["value"])
            except TimeoutError:
                print(".")
                tries += 1

        await self.send_packet(
            real_time_heart_rate.STOP_SPO2_PACKET,
        )
        return valid_spo2

    async def set_time(self):
        await self.send_packet(set_time.set_time_packet())

    async def blink_twice(self):
        await self.send_packet(blink_twice.BLINK_TWICE_PACKET)

    async def get_device_info(self):
        client = self.bleak_client
        data = {}
        device_info_service = client.services.get_service(DEVICE_INFO_UUID)
        assert device_info_service

        hw_info_char = device_info_service.get_characteristic(DEVICE_HW_UUID)
        assert hw_info_char
        hw_version = await client.read_gatt_char(hw_info_char)
        data["hw_version"] = hw_version.decode("utf-8")

        fw_info_char = device_info_service.get_characteristic(DEVICE_FW_UUID)
        assert fw_info_char
        fw_version = await client.read_gatt_char(fw_info_char)
        data["fw_version"] = fw_version.decode("utf-8")

        return data

    async def get_heart_rate_log(
        self, target: datetime | None = None
    ) -> heart_rate.HeartRateLog:
        if target is None:
            target = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0)
        await self.send_packet(heart_rate.read_heart_rate_packet(target))
        data = await asyncio.wait_for(
            self.queues[heart_rate.CMD_READ_HEART_RATE].get(), timeout=2
        )
        return data
