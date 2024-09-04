"""
The smart ring has it's own internal clock that is used to determine what time a given heart rate or step took
place for accurate counting.

We always set the time in UTC.
"""

from datetime import datetime, timezone
import logging

from colmi_r02_client.packet import make_packet

logger = logging.getLogger(__name__)

CMD_SET_TIME = 1


def set_time_packet(target: datetime) -> bytearray:
    if target.tzinfo != timezone.utc:
        logger.info("Converting target time to utc")
        target = target.astimezone(tz=timezone.utc)

    assert target.year >= 2000
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
    assert b < 100
    assert b >= 0

    tens = b // 10
    ones = b % 10
    return (tens << 4) | ones


def parse_set_time_packet(packet: bytearray) -> dict[str, bool | int]:
    """
    Parse the response to the set time packet which is some kind of capability response.

    It seems useless. It does correctly say avatar is not supported and that heart rate is supported.
    But it also says there's wechat support and it supports 20 contacts.

    I think this is safe to swallow and ignore.
    """
    assert packet[0] == CMD_SET_TIME
    bArr = packet[1:]
    data: dict[str, bool | int] = {}
    data["mSupportTemperature"] = bArr[0] == 1
    data["mSupportPlate"] = bArr[1] == 1
    data["mSupportMenstruation"] = True
    data["mSupportCustomWallpaper"] = (bArr[3] & 1) != 0
    data["mSupportBloodOxygen"] = (bArr[3] & 2) != 0
    data["mSupportBloodPressure"] = (bArr[3] & 4) != 0
    data["mSupportFeature"] = (bArr[3] & 8) != 0
    data["mSupportOneKeyCheck"] = (bArr[3] & 16) != 0
    data["mSupportWeather"] = (bArr[3] & 32) != 0
    data["mSupportWeChat"] = (bArr[3] & 64) == 0
    data["mSupportAvatar"] = (bArr[3] & 128) != 0
    # data["#width"] = ByteUtil.bytesToInt(Arrays.copyOfRange(bArr, 4, 6))
    # data["#height"] = ByteUtil.bytesToInt(Arrays.copyOfRange(bArr, 6, 8))
    data["mNewSleepProtocol"] = bArr[8] == 1
    data["mMaxWatchFace"] = bArr[9]
    data["mSupportContact"] = (bArr[10] & 1) != 0
    data["mSupportLyrics"] = (bArr[10] & 2) != 0
    data["mSupportAlbum"] = (bArr[10] & 4) != 0
    data["mSupportGPS"] = (bArr[10] & 8) != 0
    data["mSupportJieLiMusic"] = (bArr[10] & 16) != 0
    data["mSupportManualHeart"] = (bArr[11] & 1) != 0
    data["mSupportECard"] = (bArr[11] & 2) != 0
    data["mSupportLocation"] = (bArr[11] & 4) != 0
    data["mMusicSupport"] = (bArr[11] & 16) != 0
    data["rtkMcu"] = (bArr[11] & 32) != 0
    data["mEbookSupport"] = (bArr[11] & 64) != 0
    data["mSupportBloodSugar"] = (bArr[11] & 128) != 0
    if bArr[12] == 0:
        data["mMaxContacts"] = 20
    else:
        data["mMaxContacts"] = bArr[12] * 10
    data["bpSettingSupport"] = (bArr[13] & 2) != 0
    data["mSupport4G"] = (bArr[13] & 4) != 0
    data["mSupportNavPicture"] = (bArr[13] & 8) != 0
    data["mSupportPressure"] = (bArr[13] & 16) != 0
    data["mSupportHrv"] = (bArr[13] & 32) != 0

    return data
