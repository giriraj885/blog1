from datetime import datetime, timedelta
import datetime as dt

def incrementDateTime(datetime_obj, value):
    return datetime_obj + timedelta(minutes=value)

def getTodayDate():
    return dt.date.today()

def get_now():
    return datetime.now().time()