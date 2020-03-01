from datetime import datetime, timedelta
import datetime as dt
import string
from base import constants
import random

def incrementDateTime(datetime_obj, value):
    return datetime_obj + timedelta(minutes=value)

def getTodayDate():
    return dt.date.today()

def get_now():
    return datetime.now().time()

def randomGeneratorCode(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))

def datetimeToStringDateTime(date, format):
    return date.strftime(format)

def randomString():
    string = datetime.now()
    return string.strftime("%Y" "%m" "%d" "%H" "%M" "%S" "%m") + str(random.randint(1000,9999))
