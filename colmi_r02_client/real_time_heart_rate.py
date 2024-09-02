"""
This covers commands for starting and stopping the real time
heart rate and blood oxygen (SPO2) measurements, and parsing the results
"""

from colmi_r02_client.packet import make_packet

CMD_REAL_TIME_HEART_RATE = 30  # 0x1E
CMD_START_HEART_RATE = 105  # 0x69
CMD_STOP_HEART_RATE = 106  # 0x6A


START_HEART_RATE_PACKET = make_packet(
    CMD_START_HEART_RATE,
    bytearray(b"\x01\x00"),
)  # why is this backwards?
CONTINUE_HEART_RATE_PACKET = make_packet(CMD_REAL_TIME_HEART_RATE, bytearray(b"3"))
STOP_HEART_RATE_PACKET = make_packet(CMD_STOP_HEART_RATE, bytearray(b"\x01\x00\x00"))

START_SPO2_PACKET = make_packet(CMD_START_HEART_RATE, bytearray(b"\x03\x25"))
STOP_SPO2_PACKET = make_packet(CMD_STOP_HEART_RATE, bytearray(b"\x03\x00\x00"))


def parse_heart_rate(packet: bytearray) -> dict[str, int]:
    """Parses the heart rate and spo2 packets"""
    return {
        "type": packet[1],
        "error_code": packet[2],
        "value": packet[3],
    }
