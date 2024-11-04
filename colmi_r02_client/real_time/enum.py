from enum import IntEnum

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

REAL_TIME_MAPPING = {
    "heart-rate": RealTimeReading.HEART_RATE,
    "blood-pressure": RealTimeReading.BLOOD_PRESSURE,
    "spo2": RealTimeReading.SPO2,
    "fatigue": RealTimeReading.FATIGUE,
    "health-check": RealTimeReading.HEALTH_CHECK,
    "ecg": RealTimeReading.ECG,
    "pressure": RealTimeReading.PRESSURE,
    "blood-sugar": RealTimeReading.BLOOD_SUGAR,
    "hrv": RealTimeReading.HRV,
}
