"""
Heart rate log settings for controlling if the ring should record heart rate periodically, and if so how often to record.

An odd packet set up as it's either a query for the current settings or trying to set the settings.

I don't know what byte 1 in the response is.
"""

from dataclasses import dataclass
import logging

from colmi_r02_client.packet import make_packet

CMD_HEART_RATE_LOG_SETTINGS = 22  # 0x16

READ_HEART_RATE_LOG_SETTINGS_PACKET = make_packet(CMD_HEART_RATE_LOG_SETTINGS, bytearray(b"\x01"))

logger = logging.getLogger(__name__)


@dataclass
class HeartRateLogSettings:
    enabled: bool
    interval: int
    """Interval in minutes"""


def parse_heart_rate_log_settings(packet: bytearray) -> HeartRateLogSettings:
    r"""
    example: bytearray(b'\x16\x01\x01<\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00T')
    """
    assert packet[0] == CMD_HEART_RATE_LOG_SETTINGS

    raw_enabled = packet[2]
    if raw_enabled == 1:
        enabled = True
    elif raw_enabled == 2:
        enabled = False
    else:
        logger.warning(f"Unexpacted value in enabled byte {raw_enabled}, defaulting to false")
        enabled = False

    return HeartRateLogSettings(enabled=enabled, interval=packet[3])


def hr_log_settings_packet(settings: HeartRateLogSettings) -> bytearray:
    assert 0 < settings.interval < 256, "Interal must be between 0 and 255"
    enabled = 1 if settings.enabled else 2
    sub_data = bytearray([2, enabled, settings.interval])
    return make_packet(CMD_HEART_RATE_LOG_SETTINGS, sub_data)
