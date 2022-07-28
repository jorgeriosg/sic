from datetime import datetime
import pytz
from mods.config import TIME_ZONE_CONVERSATION_HISTORY
tz = pytz.timezone(TIME_ZONE_CONVERSATION_HISTORY)


#convert unixtime -> date -> UTC -> timezone
def date_timezone_from(unix_date, timezone_date, structured_date):
    return datetime.fromtimestamp(int(unix_date),timezone_date).strftime(structured_date)

def full_date(unix_date):
    return date_timezone_from(unix_date, tz, '%d-%m-%Y %H:%M:%S')

def date(unix_date):
    return date_timezone_from(unix_date, tz, '%d-%m-%Y')

def hour(unix_date):
    return date_timezone_from(unix_date, tz, '%H:%M:%S')

def dict_full_date(unix_date):
    try:
        return { 'date':  date_timezone_from(unix_date, tz, '%d-%m-%Y'), 'hour':  date_timezone_from(unix_date, tz, '%H:%M:%S') }
    except:
        import pdb; pdb.set_trace()