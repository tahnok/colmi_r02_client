from enum import IntEnum
from dataclasses import dataclass
import logging

from colmi_r02_client.packet import make_packet

logger = logging.getLogger(__name__)

CMD_FIREHOSE = 161  # 0xa1

START_FIREHOSE_PACKET = make_packet(CMD_FIREHOSE, bytearray([4]))
STOP_FIREHOSE_PACKET = make_packet(CMD_FIREHOSE, bytearray([2]))


class Kind(IntEnum):
    SPO2 = 1
    PPG = 2
    ACCELEROMETER = 3


@dataclass
class SpO2:
    current: int
    max: int
    min: int
    diff: int


@dataclass
class PPG:
    current: int
    max: int
    min: int
    diff: int


@dataclass
class Accelerometer:
    """I think this is the x, y, z axis"""

    x: int
    y: int
    z: int


def parse_firehose(packet: bytearray) -> SpO2 | PPG | Accelerometer | None:
    r"""
    bytearray(b'\xa1\x03\x1d\t\x07\x08\xfa\x00\x00\x00\x00\x00\x00\x00\x00\xd3')
    """
    kind = packet[1]
    if kind == Kind.SPO2:
        return SpO2(
            current=(packet[2] << 8) | packet[3],
            max=packet[5],
            min=packet[7],
            diff=packet[9],
        )
    elif kind == Kind.PPG:
        return PPG(
            current=(packet[2] << 8) | packet[3],
            max=(packet[4] << 8) | packet[5],
            min=(packet[6] << 8) | packet[7],
            diff=(packet[8] << 8) | packet[9],
        )
    elif kind == Kind.ACCELEROMETER:
        x = ((packet[6] << 4) | (packet[7] & 0xF)) - (1 << 11) if packet[6] & 0x8 else ((packet[6] << 4) | (packet[7] & 0xF))
        y = ((packet[3] << 4) | (packet[3] & 0xF)) - (1 << 11) if packet[2] & 0x8 else ((packet[2] << 4) | (packet[3] & 0xF))
        z = ((packet[4] << 4) | (packet[5] & 0xF)) - (1 << 11) if packet[4] & 0x8 else ((packet[4] << 4) | (packet[5] & 0xF))
        return Accelerometer(x=x, y=y, z=z)
    else:
        logging.error(f"Unexpected kind of firehose packet {packet}")
        return None
