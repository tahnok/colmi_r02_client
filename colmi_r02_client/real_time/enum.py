from enum import IntEnum, StrEnum

class Action(IntEnum):
    START = 1
    PAUSE = 2
    CONTINUE = 3
    STOP = 4

class RealTimeReading(IntEnum):
    """
    Taken from https://colmi.puxtril.com/commands/#data-request
    """
    HEART_RATE = 1
    BLOOD_PRESSURE = 2
    SPO2 = 3
    FATIGUE = 4
    HEALTH_CHECK = 5
    # leaving this out as it's redundant
    # REAL_TIME_HEART_RATE = 6
    ECG = 7
    PRESSURE = 8
    BLOOD_SUGAR = 9
    HRV = 10

class RealTimeName(StrEnum):
    HEART_RATE = "heart-rate" # Works for R02
    SPO2 = "spo2" # Works for R02
    BLOOD_PRESSURE = "blood-pressure" # Works for R02 (not sure if it's accurate)
    FATIGUE = "fatigue" # Works for R02 (not sure if it's accurate)
    HEALTH_CHECK = "health-check" # Works for R02 (not sure if it's accurate)
    ECG = "ecg" # Works for R02 (not sure if it's accurate)
    PRESSURE = "pressure" # Works for R02 (not sure if it's accurate)
    BLOOD_SUGAR = "blood-sugar" # Works for R02 (not sure if it's accurate)
    HRV = "hrv" # Works for R02 (not sure if it's accurate)

REAL_TIME_MAPPING = {
    RealTimeName.HEART_RATE: RealTimeReading.HEART_RATE,
    RealTimeName.BLOOD_PRESSURE: RealTimeReading.BLOOD_PRESSURE,
    RealTimeName.SPO2: RealTimeReading.SPO2,
    RealTimeName.FATIGUE: RealTimeReading.FATIGUE,
    RealTimeName.HEALTH_CHECK: RealTimeReading.HEALTH_CHECK,
    RealTimeName.ECG: RealTimeReading.ECG,
    RealTimeName.PRESSURE: RealTimeReading.PRESSURE,
    RealTimeName.BLOOD_SUGAR: RealTimeReading.BLOOD_SUGAR,
    RealTimeName.HRV: RealTimeReading.HRV,
}