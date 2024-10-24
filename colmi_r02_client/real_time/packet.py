from dataclasses import dataclass

from colmi_r02_client.real_time.enum import RealTimeReading, Action
from colmi_r02_client.packet import make_packet

CMD_REAL_TIME_REQUEST = 105

@dataclass
class Reading:
    kind: RealTimeReading
    value: int

@dataclass
class ReadingError:
    kind: RealTimeReading
    code: int

def get_start_packet_for_type(measurement_type: RealTimeReading):
    return make_packet(
        CMD_REAL_TIME_REQUEST,
        bytearray([measurement_type, Action.START])
    )

def get_continue_packet_for_type(measurement_type: RealTimeReading):
    return make_packet(
        CMD_REAL_TIME_REQUEST,
        bytearray([measurement_type, Action.CONTINUE])
    )

def get_end_packet_for_type(measurement_type: RealTimeReading):
    return make_packet(
        CMD_REAL_TIME_REQUEST,
        bytearray([measurement_type, Action.STOP])
    )

def parse_heart_rate(packet: bytearray) -> Reading | ReadingError:
    """Parses the heart rate and spo2 packets"""

    assert packet[0] == CMD_REAL_TIME_REQUEST

    kind = packet[1]
    error_code = packet[2]
    if error_code != 0:
        return ReadingError(kind=kind, code=error_code)

    return Reading(kind=packet[1], value=packet[3])
