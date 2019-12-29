from django.forms.models import model_to_dict
from datetime import datetime, timedelta
from otslib.utils import constants
import base64
import string
import random
import sys
import datetime as dt
from dateutil import parser
import pytz
import calendar

def increment_months(sourcedate,months):
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year, month)[1])
    return dt.date(year, month, day)

def get_time_difference(clientDate):
    date = getTodayDate()    
    return time_count((date - clientDate.date()).days)

def time_count(days):
    y = 365
    y2 = 31
    remainder = days % y
    day = remainder % y2
    year = (days - remainder) / y
    month = int((remainder - day) / y2)

    if(year !=0 and month !=0):
      return str(year) + " years & " + str(month) +" months"

    elif(year ==0 and month ==0 and day !=0):
     return str(day) +" days"

    elif(year ==0 and month !=0 and day !=0):
      return str(month) + " months & "+ str(day) +" days"

    elif(year !=0 and month ==0 and day !=0):
      return str(year) + " years & "+ str(day) +" days"

    elif(year !=0 and month !=0 and day !=0):
      return str(year) + " years & "+ str(month) + " months & "+ str(day) +" days"

    elif(year ==0 and month ==0 and day ==0):
      return str(day) +" days"

    elif(year == 0 and  month !=0 and day ==0):
      return str(month) +" month"
    return ''

def getTodayDate():
    return dt.date.today()

def get_now():
    return datetime.now().time()

def count_occurences(key, value, category, dict_list):
    counter=0
    for d in dict_list:
        if key in d and 'category' in d:
            if d[key]==value and d['category']==category:
                counter += 1
    return counter

def encode(string1):
    return base64.b64encode(string1)

def decode(string):
    return string.decode('base64')

def convertModelObjectToDict(obj):
    return model_to_dict(obj)

def convertModelObjectListToDict(obj_list):
    model_list = []
    for obj in obj_list:
        model_list.append(convertModelObjectToDict(obj))
    return model_list

def getPositiveResponse(msg, data={}):
    response = {}
    response['status'] = constants.SUCCESS
    response['message'] = msg
    response['result'] = data
    response['statusCode'] = constants.SUCESS_RESPONSE_CODE
    return response

def getNegativeResponse(msg, status_code=200, result={}):
    response = {}
    response['status'] = constants.FAIL
    response['message'] = msg
    response['result'] = result
    response['statusCode'] = status_code
    return response

def isListNoneOrEmpty(data_list):
    try:
        if data_list == None or len(data_list) <= 0:
            return True
        else:
            return False
    except:
        return True

def isValueNoneOrEmpty(string):
    if string is None or string == '':
        return True
    return False

def todayDate():
    return datetime.now()

def stringToDate(string):
    try:
        date = datetime.strptime(string, '%Y-%m-%d')
        return date
    except:
        return False    

def stringDateTimeToDateTime(string, format):
    try:
        date = datetime.strptime(string, format)
        return date
    except:
        return False    

def stringTime12HRToTime(string):
    try:
        time = datetime.strptime(string, '%I:%M %p')
        return time
    except:
        return False    

def DateTimeToString(date):
    return date.strftime('%d-%m-%Y')

def datetimeToStringDateTime(date, format):
    return date.strftime(format)

def randomGeneratorCode(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))
    
def incrementDateTime(datetime_obj, value):
    return datetime_obj + timedelta(minutes=value)

def decrementDateTime(datetime_obj, value):
    return datetime_obj - timedelta(minutes=value)

def incrementDate(date_obj, value):
    return date_obj + timedelta(days=value)

def getMinuteFromDay(day):
    return day * 24 * 60

def getStringSize(string, size_type='KB'):
    try:
        return sys.getsizeof(string) / 1000.0
    except:
        return False

def getErrorMessage(error_dict):
    field = next(iter(error_dict))
    response = error_dict[next(iter(error_dict))]
    if isinstance(response, dict):
        response = getErrorMessage(response)
    elif isinstance(response, list):
        response_message = response[0]
        if isinstance(response_message, dict):
            response = getErrorMessage(response_message)
        else:
            response = field + " : " + response[0]
    return response

def getFirstErrorMessage(error_dict):
    response = error_dict[next(iter(error_dict))]
    if isinstance(response, dict):
        response = getFirstErrorMessage(response)
    elif isinstance(response, list):
        response = response[0]
        if isinstance(response, dict):
            response = getFirstErrorMessage(response)
    return response

def getPKErrorMessage(error_dict):
    field = next(iter(error_dict))
    response = error_dict[next(iter(error_dict))]
    if isinstance(response, dict):
        response = getErrorMessage(response)
    elif isinstance(response, list):
        value  = response[0].split('\"')[1]
        response = "Invalid value " + value + " for " + field + "."
    return response

def randomString():
    string = datetime.now()
    return string.strftime("%Y" "%m" "%d" "%H" "%M" "%S" "%m") + str(random.randint(1000,9999))

def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)

def getUTCDateTime():
    return pytz.utc.localize(datetime.utcnow()).replace(microsecond=0)

def convertDateTimeToISOFormat(datetime_obj):
    return datetime_obj.isoformat()

def convertISODateTimeStringToUTC(iso_date_time):
    format = '%Y-%m-%dT%H:%M:%S%z'
    utc_date_time = parser.parse(iso_date_time)
    return  utc_date_time.replace(tzinfo=pytz.utc) - utc_date_time.utcoffset()
