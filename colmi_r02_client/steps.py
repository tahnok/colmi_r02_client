from dataclasses import dataclass

from colmi_r02_client.packet import make_packet

CMD_GET_STEP_SOMEDAY = 67  # 0x43

GET_TODAY_STEPS_PACKET = make_packet(
    CMD_GET_STEP_SOMEDAY, bytearray(b"\x00\x0f\x00\x5f\x01")
)


@dataclass
class SportDetail:
    year: int
    month: int
    day: int
    time_index: int
    calories: int
    steps: int
    distance: int


class SportDetailParser:
    r"""
    Parse SportDetailPacket, of which there will be several

    example data:
    bytearray(b'C\xf0\x05\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x009')
    bytearray(b'C#\x08\x13\x10\x00\x05\xc8\x000\x00\x1b\x00\x00\x00\xa9')
    bytearray(b'C#\x08\x13\x14\x01\x05\xb6\x18\xaa\x04i\x03\x00\x00\x83')
    bytearray(b'C#\x08\x13\x18\x02\x058\x04\xe1\x00\x95\x00\x00\x00R')
    bytearray(b'C#\x08\x13\x1c\x03\x05\x05\x02l\x00H\x00\x00\x00`')
    bytearray(b'C#\x08\x13L\x04\x05\xef\x01c\x00D\x00\x00\x00m')
    """

    def __init__(self):
        self.reset()

    def reset(self) -> None:
        self.new_calorie_protocol = False
        self.index = 0
        self.details: list[SportDetail] = []

    def parse(self, packet: bytearray) -> None:
        assert len(packet) == 16
        assert packet[0] == CMD_GET_STEP_SOMEDAY

        if self.index == 0 and packet[1] == 255:
            self.reset()
            return

        if self.index == 0 and packet[1] == 240:
            if packet[3] == 1:
                self.new_calorie_protocol = True
            self.index += 1
        else:
            year = bcd_to_decimal(packet[1]) + 2000
            month = bcd_to_decimal(packet[2])
            day = bcd_to_decimal(packet[3])
            time_index = packet[4]
            calories = packet[7] | (packet[8] << 8)
            if self.new_calorie_protocol:
                calories *= 10
            steps = packet[9] | (packet[10] << 8)
            distance = packet[11] | (packet[12] << 8)

            details = SportDetail(
                year=year,
                month=month,
                day=day,
                time_index=time_index,
                calories=calories,
                steps=steps,
                distance=distance,
            )
            print("Details: ", details)
            self.details.append(details)

            self.index += 1
            if packet[5] == packet[6] - 1:
                self.reset()


def bcd_to_decimal(b: int) -> int:
    return (((b >> 4) & 15) * 10) + (b & 15)
