"""
Get the battery level and charging status.
"""

from dataclasses import dataclass

from colmi_r02_client.packet import make_packet

CMD_BATTERY = 3

BATTERY_PACKET = make_packet(CMD_BATTERY)


@dataclass
class BatteryInfo:
    battery_level: int
    charging: bool


def parse_battery(packet: bytearray) -> BatteryInfo:
    r"""
    example: bytearray(b'\x03@\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00C')
    """
    return BatteryInfo(battery_level=packet[1], charging=bool(packet[2]))
