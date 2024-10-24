from enum import IntEnum, StrEnum

class Action(IntEnum):
    START = 1
    PAUSE = 2
    CONTINUE = 3
    STOP = 4

class RealTimeReading(IntEnum):
    HEART_RATE = 1
    BLOOD_PRESSURE = 2
    SPO2 = 3
    FATIGUE = 4
    HEALTH_CHECK = 5
    REAL_TIME_HEART_RATE = 6
    ECG = 7
    PRESSURE = 8
    BLOOD_SUGAR = 9
    HRV = 10

class RealTimeName(StrEnum):
    HEART_RATE = "heart-rate"
    SPO2 = "spo2"
    BLOOD_PRESSURE = "blood-pressure"
    FATIGUE = "fatigue"
    HEALTH_CHECK = "health-check"
    REAL_TIME_HEART_RATE = "real-time-heart-rate"
    ECG = "ecg"
    PRESSURE = "pressure"
    BLOOD_SUGAR = "blood-sugar"
    HRV = "hrv"

REAL_TIME_MAPPING = {
    RealTimeName.HEART_RATE: RealTimeReading.HEART_RATE,
    RealTimeName.BLOOD_PRESSURE: RealTimeReading.BLOOD_PRESSURE,
    RealTimeName.SPO2: RealTimeReading.SPO2,
    RealTimeName.FATIGUE: RealTimeReading.FATIGUE,
    RealTimeName.HEALTH_CHECK: RealTimeReading.HEALTH_CHECK,
    RealTimeName.REAL_TIME_HEART_RATE: RealTimeReading.REAL_TIME_HEART_RATE,
    RealTimeName.ECG: RealTimeReading.ECG,
    RealTimeName.PRESSURE: RealTimeReading.PRESSURE,
    RealTimeName.BLOOD_SUGAR: RealTimeReading.BLOOD_SUGAR,
    RealTimeName.HRV: RealTimeReading.HRV,
}