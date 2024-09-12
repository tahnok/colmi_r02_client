"""
Heart rate log settings for controlling if the ring should record heart rate periodically, and if so how often to record.

An odd packet set up as it's either a query for the current settings or trying to set the settings.
"""

from dataclasses import dataclass

from colmi_r02_client.packet import make_packet

CMD_HEART_RATE_LOG_SETTINGS = 22  # 0x16

READ_HEART_RATE_LOG_SETTINGS_PACKET = make_packet(CMD_HEART_RATE_LOG_SETTINGS, bytearray(b"\x01"))


@dataclass
class HeartRateLogSettings:
    enabled: bool
    interval: int
    """Interval in unknown units"""


def parse_heart_rate_log_settings(packet: bytearray) -> HeartRateLogSettings:
    r"""
    example: bytearray(b'\x16\x01\x01<\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00T')
    """
    assert packet[0] == CMD_HEART_RATE_LOG_SETTINGS

    return HeartRateLogSettings(enabled=bool(packet[1]), interval=packet[2])
