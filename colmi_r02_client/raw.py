"""
Get 'raw' data from the ring using an undocumented debug mode I think.

Hat tip to ATC1441 for finding this with reverse engineering
"""

import logging

from colmi_r02_client.packet import make_packet

CMD_RAW = 161  # 0xA10404
# can also try A101

START_RAW_PACKET = make_packet(CMD_RAW, bytearray(b"\x04\x04"))
STOP_RAW_PACKET = make_packet(CMD_RAW, bytearray(b"\x02"))

logger = logging.getLogger(__name__)


def parse_raw(packet: bytearray) -> None:
    kind = packet[1]
    if kind == 1:
        # raw blood
        raw_blood = packet[2] << 8 | packet[3]
        max_1 = packet[5]
        max_2 = packet[7]
        max_3 = packet[9]
        logger.info(f"{raw_blood=}, {max_1=}, {max_2=}, {max_3=}")
    elif kind == 2:
        logger.info("HRS")
    elif kind == 3:
        logger.info("accelerometer")
    else:
        logger.warning(f"idk what this is {packet=}")
