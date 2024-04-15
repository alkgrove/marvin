# return string of human readible text for timer interval given ticks in seconds
# options are precision which can be days, hours, minutes, seconds or auto defaulting to seconds
# precision of auto will set precision to seconds if < 60s, minutes if < 3600, etc
# and round is either True for rounding up or False for truncating (default)
def periodToString(period, precision="seconds", round=False, short=False):
    # convert ticks in seconds to days, hours, minutes, seconds
    days = int(period / 86400)
    hours_remaining = period % 86400
    hours = int(hours_remaining / 3600)
    minutes_remaining = hours_remaining % 3600
    minutes = int(minutes_remaining / 60)
    seconds = minutes_remaining % 60
    if (precision == 'auto'):
        if (period < 60):
            precision = 'seconds'
        elif (period < 3600):
            precision = 'minutes'
        elif (period < 86400):
            precision = 'hours'
        else:
            precision = 'days'
    # take care of precision, we use setting a value to zero to not print it
    if (precision == 'minutes'):
        if (round): # round up seconds
            if (seconds >= 30):
                minutes += 1
                seconds = 0
                if (minutes > 59):
                    hours += 1
                    minutes = 0
                if (hours > 23):
                    days += 1
                    hours = 0
        seconds = 0
        if (minutes == 0):
            return "under one minute"
    elif (precision == 'hours'):
        if (round):
            if (minutes >= 30):
                hours += 1
                minutes = 0
                if (hours > 23):
                    days += 1
                    hours = minutes = 0
        seconds = minutes = 0
        if(hours == 0):
            return "under one hour"
    elif (precision == 'days'):
        if (round):
            if (hours >= 12):
                days += 1
                hours = 0
        hours = seconds = minutes = 0
        if (days == 0):
            return "under one day"
    # convert to human readible string
    str = ""
    if (days > 0):
        str += f"{days}{'day' if (short) else (' days' if (days > 1) else ' day')}"
    if (hours > 0):
        if (not short and (days > 0)):
            str += ' '
        str += f"{hours}{'hr' if (short) else (' hours' if (hours > 1) else ' hour')}"
    if (minutes > 0):
        if (not short and ((hours > 0) or (days > 0))):
            str += ' and '
        str += f"{minutes}{'min' if (short) else (' minutes' if (minutes > 1) else ' minute')}"
    if (seconds > 0):
        if (not short and ((minutes > 0) or (hours > 0) or (days > 0))):
            str += ' '
        str += f"{seconds}{'s' if (short) else (' seconds' if (seconds > 1) else ' second')}"
    return str
    
