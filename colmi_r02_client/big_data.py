
import logging
from dataclasses import dataclass
from typing import List
from colmi_r02_client.packet import make_packet

CMD_BIG_DATA = 188
BIG_DATA_SLEEP = 39

logger = logging.getLogger(__name__)


def read_sleep_bigdata_packet() -> bytearray:
    """
    Build BigDataRequest packet for sleep:
    struct BigDataRequest {
        uint8_t bigDataMagic = 188;
        uint8_t dataId = 39;
        uint16_t dataLen = 0;
        uint16_t crc16 = 0xFFFF;
    }
    """
    packet = bytearray([
        BIG_DATA_SLEEP,
        0x00, 0x00, # dataLen = 0
        0xFF, 0xFF  # crc16 = 0xFFFF
    ])
    return make_packet(CMD_BIG_DATA, packet)


def parse_bigdata_response(packet: bytearray):
    """
    struct BigDataResponse {
        uint8_t bigDataMagic = 188;
        uint8_t dataId;
        uint16_t dataLen;
        uint16_t crc16;
        // Variable data length
    }
    """
    if len(packet) < 7 or packet[0] != CMD_BIG_DATA:
        logger.warning("Invalid BigData packet")
        return None
    if packet[1] == BIG_DATA_SLEEP:
        return parse_bigdata_sleep_response(packet)
    else:
        logger.warning(f"Unhandled BigData packet dataId: {packet[1]}")
        return None
    

# Dataclasses for sleep data
@dataclass
class SleepPeriod:
    type: int
    minutes: int

@dataclass
class SleepDay:
    daysAgo: int
    sleepStart: int
    sleepEnd: int
    periods: List[SleepPeriod]

def parse_bigdata_sleep_response(packet: bytearray) -> List[SleepDay] | None:
    """
    struct SleepData {
        uint8_t bigDataMagic = 188;
        uint8_t sleepId = 39;
        uint16_t dataLen;
        uint16_t crc16;
        uint8_t sleepDays;
        SleepDay days[];
    }
    struct SleepDay {
        uint8_t daysAgo;
        uint8_t curDayBytes;
        int16_t sleepStart; // Minutes after midnight
        int16_t sleepEnd; // Minutes after midnight
        SleepPeriod sleepPeriods[];
    }
    struct SleepPeriod {
        SleepType type;
        uint8_t minutes;
    }
    enum SleepType : uint8_t {
        NODATA = 0,
        ERROR = 1,
        LIGHT = 2,
        DEEP = 3,
        REM = 4,
        AWAKE = 5,
    }
    """
    if len(packet) < 7 or packet[0] != CMD_BIG_DATA or packet[1] != BIG_DATA_SLEEP:
        logger.warning("Invalid BigData sleep packet")
        return None
    data_len = int.from_bytes(packet[2:4], 'little')
    crc16 = int.from_bytes(packet[4:6], 'little')
    sleep_days = packet[6]
    idx = 7
    days: List[SleepDay] = []
    for _ in range(sleep_days):
        if idx + 6 > len(packet):
            logger.warning("Packet too short for another SleepDay")
            break
        daysAgo = packet[idx]
        curDayBytes = packet[idx+1]
        sleepStart = int.from_bytes(packet[idx+2:idx+4], 'little', signed=True)
        sleepEnd = int.from_bytes(packet[idx+4:idx+6], 'little', signed=True)
        periods: List[SleepPeriod] = []
        period_idx = idx+6
        while period_idx < idx+1+curDayBytes:
            if period_idx+2 > len(packet):
                break
            sleep_type = packet[period_idx]
            minutes = packet[period_idx+1]
            periods.append(SleepPeriod(type=sleep_type, minutes=minutes))
            period_idx += 2
        days.append(SleepDay(
            daysAgo=daysAgo,
            sleepStart=sleepStart,
            sleepEnd=sleepEnd,
            periods=periods
        ))
        idx += 1 + curDayBytes
    return days
