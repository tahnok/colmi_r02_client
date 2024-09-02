from bleak import BleakClient
from bleak.backends.characteristic import BleakGATTCharacteristic


def make_packet(command_key: int, sub_data: bytearray | None = None) -> bytearray:
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


async def send_packet(
    client: BleakClient,
    rx_char: BleakGATTCharacteristic,
    packet: bytearray,
) -> None:
    await client.write_gatt_char(rx_char, packet, response=False)
