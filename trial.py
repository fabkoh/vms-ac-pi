from dateutil.rrule import *
from datetime import *
from dateutil.parser import *

start_date = datetime(2014, 12, 31)
#print(list(rrule(freq=MONTHLY, count=4, dtstart=start_date)))
cal = (list(rrule(DAILY,dtstart=parse("19970902T090000"),until=parse("19971224T000000"))))
for i in range(len(cal)):
    print(cal[i])