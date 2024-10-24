from dataclasses import dataclass

from colmi_r02_client.real_time.enum import RealTimeReading, Action
from colmi_r02_client.packet import make_packet

CMD_START_REAL_TIME = 105
CMD_STOP_REAL_TIME = 106

@dataclass
class Reading:
    kind: RealTimeReading
    value: int

@dataclass
class ReadingError:
    kind: RealTimeReading
    code: int

def get_start_packet(reading_type: RealTimeReading):
    return make_packet(
        CMD_START_REAL_TIME,
        bytearray([reading_type, Action.START])
    )

def get_continue_packet(reading_type: RealTimeReading):
    return make_packet(
        CMD_START_REAL_TIME,
        bytearray([reading_type, Action.CONTINUE])
    )

def get_stop_packet(reading_type: RealTimeReading):
    return make_packet(
        CMD_STOP_REAL_TIME,
        bytearray([reading_type, 0, 0])
    )

def parse_real_time_reading(packet: bytearray) -> Reading | ReadingError:
    """Parses the heart rate and spo2 packets"""

    assert packet[0] == CMD_START_REAL_TIME

    kind = packet[1]
    error_code = packet[2]
    if error_code != 0:
        return ReadingError(kind=kind, code=error_code)

    return Reading(kind=packet[1], value=packet[3])
