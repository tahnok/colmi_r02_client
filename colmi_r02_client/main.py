"""
A python client for connecting to the Colmi R02 Smart ring


TODO:
    - get "Stress"
    - make nicer methods for getting data from callback
    - "scan" mode instead of hard coded address
"""

from dataclasses import dataclass
from datetime import datetime, timezone
import struct

import asyncio
from bleak import BleakClient
from bleak.backends.characteristic import BleakGATTCharacteristic


ADDRESS = "70:CB:0D:D0:34:1C"

UART_SERVICE_UUID = "6E40FFF0-B5A3-F393-E0A9-E50E24DCCA9E"
UART_RX_CHAR_UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"
UART_TX_CHAR_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"

DEVICE_INFO_UUID = "0000180A-0000-1000-8000-00805F9B34FB"
DEVICE_HW_UUID = "00002A27-0000-1000-8000-00805F9B34FB"
DEVICE_FW_UUID = "00002A26-0000-1000-8000-00805F9B34FB"

CMD_REAL_TIME_HEART_RATE = 30 # 0x1E
CMD_START_HEART_RATE = 105 # 0x69
CMD_STOP_HEART_RATE = 106 # 0x6A
CMD_BATTERY = 3
CMD_BLINK_TWICE = 16 # 0x10
CMD_GET_STEP_SOMEDAY = 67 #0x43
CMD_SET_TIME = 1
CMD_READ_HEART_RATE = 21 # 0x15

def make_packet(command_key: int, sub_data: bytearray|None = None) -> bytearray:
    packet = bytearray(16)
    packet[0] = command_key

    if sub_data:
        assert len(sub_data) <= 14
        for i in range(len(sub_data)):
            packet[i + 1] = sub_data[i]
    
    packet[-1] = crc(packet)

    return packet

def crc(packet: bytearray) -> int:
    return sum(packet) & 255

START_HEART_RATE_PACKET = make_packet(CMD_START_HEART_RATE, bytearray(b'\x01\x00')) # why is this backwards?
CONTINUE_HEART_RATE_PACKET = make_packet(CMD_REAL_TIME_HEART_RATE, bytearray(b'3'))
STOP_HEART_RATE_PACKET = make_packet(CMD_STOP_HEART_RATE, bytearray(b'\x01\x00\x00'))

START_SPO2_PACKET = make_packet(CMD_START_HEART_RATE, bytearray(b'\x03\x25'))
STOP_SPO2_PACKET = make_packet(CMD_STOP_HEART_RATE, bytearray(b'\x03\x00\x00'))

BATTERY_PACKET = make_packet(CMD_BATTERY)

BLINK_TWICE_PACKET = make_packet(CMD_BLINK_TWICE)

GET_TODAY_STEPS_PACKET = make_packet(CMD_GET_STEP_SOMEDAY, bytearray(b'\x00\x0F\x00\x5F\x01'))

def byte_to_bcd(b: int) -> int:
    assert b < 99
    assert b > 0

    tens = b // 10
    ones = b % 10
    return (tens << 4) | ones

def bcd_to_decimal(b: int) -> int:
    return (((b >> 4) & 15) * 10) + (b & 15)

def set_time_packet(target: datetime | None = None) -> bytearray:
    if target is None:
        target = datetime.now()
    data = bytearray(7)
    data[0] = byte_to_bcd(target.year % 2000)
    data[1] = byte_to_bcd(target.month)
    data[2] = byte_to_bcd(target.day)
    data[3] = byte_to_bcd(target.hour)
    data[4] = byte_to_bcd(target.minute)
    data[5] = byte_to_bcd(target.second)
    data[6] = 1 # set language to english, 0 is chinese
    return make_packet(CMD_SET_TIME, data)

def read_heart_rate_packet(target: datetime | None = None) -> bytearray:
    if target is None:
        target = datetime.now(timezone.utc).replace(hour=0,minute=0,second=0)
    data = bytearray(struct.pack("<L", int(target.timestamp())))

    return make_packet(CMD_READ_HEART_RATE, data)

async def send_packet(client: BleakClient, rx_char, packet: bytearray) -> None:
    await client.write_gatt_char(rx_char, packet, response=False)


@dataclass
class SportDetail():
    year: int
    month: int
    day: int
    time_index: int
    calories: int
    steps: int
    distance: int


class SportDetailParser():
    r"""
    Parse SportDetailPacket, of which there will be several

    example data:
    bytearray(b'C\xf0\x05\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x009')
    bytearray(b'C#\x08\x13\x10\x00\x05\xc8\x000\x00\x1b\x00\x00\x00\xa9')
    bytearray(b'C#\x08\x13\x14\x01\x05\xb6\x18\xaa\x04i\x03\x00\x00\x83')
    bytearray(b'C#\x08\x13\x18\x02\x058\x04\xe1\x00\x95\x00\x00\x00R')
    bytearray(b'C#\x08\x13\x1c\x03\x05\x05\x02l\x00H\x00\x00\x00`')
    bytearray(b'C#\x08\x13L\x04\x05\xef\x01c\x00D\x00\x00\x00m')
    """

    def __init__(self):
        self.reset()

    def reset(self):
        self.new_calorie_protocol = False
        self.index = 0
        self.details: list[SportDetail] = []

    def parse(self, packet: bytearray):
        assert len(packet) == 16
        assert packet[0] == CMD_GET_STEP_SOMEDAY

        if self.index == 0 and packet[1] == 255:
            self.reset()
            return

        if self.index == 0 and packet[1] == 240:
            if packet[3] == 1:
                self.new_calorie_protocol = True
            self.index += 1
        else:
            year = bcd_to_decimal(packet[1]) + 2000
            month = bcd_to_decimal(packet[2])
            day = bcd_to_decimal(packet[3])
            time_index = packet[4]
            calories = packet[7] | (packet[8] << 8)
            if self.new_calorie_protocol:
                calories *= 10
            steps = packet[9] | (packet[10] << 8)
            distance = packet[11] | (packet[12] << 8)

            details = SportDetail(
                    year=year,
                    month=month,
                    day=day,
                    time_index=time_index,
                    calories=calories,
                    steps=steps,
                    distance=distance
                    )
            print("Details: ", details)
            self.details.append(details)

            self.index += 1
            if packet[5] == packet[6] - 1:
                self.reset()

class DailyHeartRateParser():
    def __init__(self):
        self.reset()

    def reset(self):
        self.heart_rate_array = []
        self.m_utc_time = None
        self.size = 0
        self.index = 0
        self.end = False
        self.range = 5

    def is_today(self) -> bool:
        d = self.m_utc_time
        if d is None:
            return False
        now = datetime.now() # use local time
        return d.year == now.year and d.month == now.month and d.day == now.day

    def parse(self, packet: bytearray) -> None:
        r"""
        first byte of packet should always be CMD_READ_HEART_RATE (21)
        second byte is the sub_type

        sub_type 0 contains the lengths of things
        byte 2 is the number of expected packets after this.

        example: bytearray(b'\x15\x00\x18\x05\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x002'),


        """

        sub_type = packet[1]
        if sub_type == 255 or (self.is_today() and sub_type == 23):
            # reset?
            return
        if sub_type == 0:
            self.end = False
            self.size = packet[2] #number of expected readings or packets?
            self.range = packet[3]
            self.heart_rate_array = [-1] * (self.size * 13) # don't really need this but...
        elif sub_type == 1:
            # next 4 bytes are a timestamp
            ts = struct.unpack_from("<l", packet, offset=2)[0]
            self.m_utc_time = datetime.fromtimestamp(ts, timezone.utc)
            #TODO timezone?

            # remaining 16 - type - subtype - 4 - crc = 9
            self.heart_rate_array[0:9] = list(packet[6:-1]) # I think this is the rest?
            self.index += 9
        else:
            b = len(self.heart_rate_array)
            print("packet", list(packet[2:15]))
            print("slice", self.heart_rate_array[self.index:self.index+13])
            print([x for x in self.heart_rate_array[self.index:self.index+13] if x != -1])
            assert not [x for x in self.heart_rate_array[self.index:self.index+13] if x != -1]
            self.heart_rate_array[self.index:self.index+13] = list(packet[2:15])
            assert b == len(self.heart_rate_array)
            self.index += 13
            if sub_type == self.size - 1:
                self.end = True
                # probaby do a reset
        self.end = True
        # possibly do a reset
        print("post self", self)


def parse_heart_rate(packet: bytearray) -> dict[str, int]:
    return {
            "type": packet[1],
            "error_code": packet[2],
            "value": packet[3],
            }

def empty_parse(_packet: bytearray) -> None:
    """Used for commands that we expect a response, but there's nothing in the response"""
    return None

def parse_battery(packet: bytearray) -> dict[str, int]:
    r"""
    example: bytearray(b'\x03@\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00C')
    """
    return {
            "battery_level": packet[1],
            "charging": bool(packet[2]),
            }

def log_packet(packet: bytearray) -> None:
    print("received: ", packet)

# these are commands that we expect to have a response returned for
COMMAND_HANDLERS = {
        CMD_BATTERY: parse_battery,
        CMD_START_HEART_RATE: parse_heart_rate,
        CMD_STOP_HEART_RATE: empty_parse,
        CMD_GET_STEP_SOMEDAY: SportDetailParser().parse,
    }

async def get_heart_rate(client, rx_char, queues: dict[int, asyncio.Queue]) -> None:
    await send_packet(client, rx_char, START_HEART_RATE_PACKET)
    print("wrote HR reading packet, waiting...")

    valid_hr = []
    tries = 0
    while len(valid_hr) < 6 and tries < 20:
        try:
            data = await asyncio.wait_for(queues[CMD_START_HEART_RATE].get(), 2)
            if data["error_code"] == 1:
                print("No heart rate detected, probably not on")
                break
            if data["value"] != 0:
                valid_hr.append(data["value"])
        except TimeoutError:
            print(".")
            tries += 1
            await client.write_gatt_char(rx_char, CONTINUE_HEART_RATE_PACKET, response=False)

    await client.write_gatt_char(rx_char, STOP_HEART_RATE_PACKET, response=False)
    print(valid_hr)


async def get_spo2(client, rx_char) -> None:
    await client.write_gatt_char(rx_char, START_SPO2_PACKET, response=False)
    print("wrote SPO2 reading packet, waiting...")

    for _ in range(16):
        await asyncio.sleep(2)
        print(".")

    await client.write_gatt_char(rx_char, STOP_SPO2_PACKET, response=False)

async def get_battery(client, rx_char, queues: dict[int, asyncio.Queue]):
    await send_packet(client, rx_char, BATTERY_PACKET)
    return await queues[CMD_BATTERY].get()


async def get_device_info(client: BleakClient):
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

async def set_time(client: BleakClient, rx_char):
    await send_packet(client, rx_char, set_time_packet())

async def main():
    print("Connecting...")

    queues = { cmd: asyncio.Queue() for cmd in COMMAND_HANDLERS.keys() }

    def handle_rx(_: BleakGATTCharacteristic, packet: bytearray):
        packet_type = packet[0]
        assert packet_type < 127, f"Packet has error bit set {packet}"

        if packet_type in COMMAND_HANDLERS:
            queues[packet_type].put_nowait(COMMAND_HANDLERS[packet_type](packet))
        else:
            print("Did not expect this packet", packet)

    async with BleakClient(ADDRESS) as client:
        print("Connected")
        print("Device info: ", await get_device_info(client))

        nus = client.services.get_service(UART_SERVICE_UUID)
        assert nus
        rx_char = nus.get_characteristic(UART_RX_CHAR_UUID)
        assert rx_char

        await client.start_notify(UART_TX_CHAR_UUID, handle_rx)

        print("battery:", await get_battery(client, rx_char, queues))

        #await get_heart_rate(client, rx_char, queues)
        #await set_time(client, rx_char)
        target = datetime(2024,8,10,0,0,0,0,tzinfo=timezone.utc)
        await send_packet(client, rx_char, read_heart_rate_packet(target))

        #await client.write_gatt_char(rx_char, GET_TODAY_STEPS_PACKET, response=False)
        await asyncio.sleep(2)


def run():
    asyncio.run(main())

if __name__ == '__main__':
    run()


