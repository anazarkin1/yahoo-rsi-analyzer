__author__ = 'alex'

# used to sort dates
from datetime import datetime

def get_string_to_date_object(str_to_parse, format_string="%b %d %Y"):
    if type(str_to_parse) == datetime:
        return str_to_parse
    return datetime.strptime(str_to_parse, format_string)

def get_sorted_dates_array(array_to_sort, reverse=False):

    dates_to_sort=[]
    for date_to_sort in array_to_sort:
        dates_to_sort.append(get_string_to_date_object(date_to_sort))
    return sorted(dates_to_sort, reverse=reverse)

def get_date_to_string(time_object, format_string="%b %d %Y"):
    # NOTE: Yahoo uses dates in format "Dec 1 2012", not "Dec 01 2012"
    # that's why we replace ' 0' with ' '
    return time_object.strftime(format_string).replace(' 0', ' ')


def prev_month(sourcedatetime):
    this_month=sourcedatetime.month
    return this_month -1 or 12

