from datetime import datetime

from colmi_r02_client.packet import make_packet


CMD_SET_TIME = 1


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
    data[6] = 1  # set language to english, 0 is chinese
    return make_packet(CMD_SET_TIME, data)


def byte_to_bcd(b: int) -> int:
    assert b < 99
    assert b > 0

    tens = b // 10
    ones = b % 10
    return (tens << 4) | ones
