import pytz
from datetime import datetime


def get_datetime_now_jkt():
    TIMEZONE_JKT = pytz.timezone(zone='Asia/Jakarta')
    return datetime.now(tz=TIMEZONE_JKT)
