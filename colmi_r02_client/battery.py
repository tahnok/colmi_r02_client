import asyncio

from colmi_r02_client.packet import make_packet

CMD_BATTERY = 3

BATTERY_PACKET = make_packet(CMD_BATTERY)

def parse_battery(packet: bytearray) -> dict[str, int]:
    r"""
    example: bytearray(b'\x03@\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00C')
    """
    return {
            "battery_level": packet[1],
            "charging": bool(packet[2]),
            }
