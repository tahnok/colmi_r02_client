"""This is called the DailyHeartRate in Java."""

from datetime import datetime, timezone, timedelta
from dataclasses import dataclass
import logging
import struct

from colmi_r02_client.packet import make_packet
from colmi_r02_client import date_utils

CMD_READ_HEART_RATE = 21  # 0x15

logger = logging.getLogger(__name__)


def read_heart_rate_packet(target: datetime) -> bytearray:
    """target datetime should be at midnight for the day of interest"""
    data = bytearray(struct.pack("<L", int(target.timestamp())))

    return make_packet(CMD_READ_HEART_RATE, data)


def _add_times(heart_rates: list[int], ts: datetime) -> list[tuple[int, datetime]]:
    assert len(heart_rates) == 288, "Need exactly 288 points at 5 minute intervals"
    result = []
    m = datetime(ts.year, ts.month, ts.day, tzinfo=ts.tzinfo)
    five_min = timedelta(minutes=5)
    for hr in heart_rates:
        result.append((hr, m))
        m += five_min

    return result


@dataclass
class HeartRateLog:
    heart_rates: list[int]
    timestamp: datetime
    size: int
    index: int
    range: int

    def heart_rates_with_times(self):
        return _add_times(self.heart_rates, self.timestamp)


class NoData:
    """Returned when there's no heart rate data"""


class HeartRateLogParser:
    def __init__(self):
        self.reset()

    def reset(self) -> None:
        self._raw_heart_rates: list[int] = []
        self.timestamp: datetime | None = None
        self.size = 0
        self.index = 0
        self.end = False
        self.range = 5

    def is_today(self) -> bool:
        d = self.timestamp
        if d is None:
            return False
        return date_utils.is_today(d)

    def parse(self, packet: bytearray) -> HeartRateLog | NoData | None:
        r"""
        first byte of packet should always be CMD_READ_HEART_RATE (21)
        second byte is the sub_type

        sub_type 0 contains the lengths of things
        byte 2 is the number of expected packets after this.

        example: bytearray(b'\x15\x00\x18\x05\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x002')
        """

        sub_type = packet[1]
        if sub_type == 255:
            logger.info("error response from heart rate log request")
            self.reset()
            return NoData()
        if self.is_today() and sub_type == 23:
            assert self.timestamp
            result = HeartRateLog(
                heart_rates=self.heart_rates,
                timestamp=self.timestamp,
                size=self.size,
                range=self.range,
                index=self.index,
            )
            self.reset()
            return result
        if sub_type == 0:
            self.end = False
            self.size = packet[2]  # number of expected packets
            self.range = packet[3]
            self._raw_heart_rates = [-1] * (self.size * 13)
            return None
        elif sub_type == 1:
            # next 4 bytes are a timestamp
            ts = struct.unpack_from("<l", packet, offset=2)[0]
            self.timestamp = datetime.fromtimestamp(ts, timezone.utc)
            # TODO timezone?

            # remaining 16 - type - subtype - 4 - crc = 9
            self._raw_heart_rates[0:9] = list(packet[6:-1])
            self.index += 9
            return None
        else:
            self._raw_heart_rates[self.index : self.index + 13] = list(packet[2:15])
            self.index += 13
            if sub_type == self.size - 1:
                assert self.timestamp
                result = HeartRateLog(
                    heart_rates=self.heart_rates,
                    timestamp=self.timestamp,
                    size=self.size,
                    range=self.range,
                    index=self.index,
                )
                self.reset()
                return result
            else:
                return None

    @property
    def heart_rates(self) -> list[int]:
        """
        Normalize and clean heart rate logs

        I don't really understand why it's implemented this way.
        I think to handle cases where there's a bit more or less data than expected
        and if there's bad values in time slots that shouldn't exist yet because those
        slots are in the future.
        """

        hr = self._raw_heart_rates.copy()

        if len(self._raw_heart_rates) > 288:
            hr = hr[0:288]
        elif len(self._raw_heart_rates) < 288:
            hr.extend([0] * (288 - len(hr)))

        # TODO see if we can remove this
        # need a good reason why parsing should depend on the day
        # index might be good enough to indicate how much "valid" data we've gotten
        if self.is_today():
            m = date_utils.minutes_so_far(datetime.now(tz=timezone.utc)) // 5
            hr[m:] = [0] * len(hr[m:])

        return hr
