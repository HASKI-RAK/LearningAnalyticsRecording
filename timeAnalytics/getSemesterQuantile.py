from datetime import datetime
from enum import Enum
import json


with open('timeAnalytics/data/config_WiSe_2425.json', 'r') as f:
    config = json.load(f)
    WINTER_START = datetime.strptime(config['WINTER_START'], "%Y-%m-%d")
    WINTER_END = datetime.strptime(config['WINTER_END'], "%Y-%m-%d")
    SUMMER_START = datetime.strptime(config['SUMMER_START'], "%Y-%m-%d")
    SUMMER_END = datetime.strptime(config['SUMMER_END'], "%Y-%m-%d")

class Quantile(Enum):
    First_3_weeks = 0
    Middle = 1
    Last_3_weeks = 2

def determine_timestamp_semester(timestamp):
    """determines the semester of a timestamp. Might need to adjust the final dates of the semester so they reflect the day of the exam

    Args:
        timestamp (int): timestamp to evaluate

    Returns:
        start and end dates for the semester of the timestamp
    """
        
    #winter_start = datetime(2024, 10, 1)
    #winter_end = datetime(2025, 2, 27) # adjust this if necessary
    #summer_start = datetime(timestamp.year, 3, 18) # adjust this if necessary
    #summer_end = datetime(timestamp.year, 7, 12) # adjust this if necessary

    if WINTER_START <= timestamp <= WINTER_END:
        return WINTER_START, WINTER_END
    elif SUMMER_START <= timestamp <= SUMMER_END:
        return SUMMER_START, SUMMER_END
    else:
        return None, None

def calculate_semester_quantiles(timestamp):
    """calculates the semster quantile for a given timestamp.
    Can either be first 3 weeks, middle of semster or last 3 weeks.
    
    Args:
        timestamp (int): a given timestamp that should be evaluated

    Returns:
        quantile: the quantile of the timestamp
        progress_percentage: the percentage of how far the semster has progressed at the timestamp
    """

    timestamp = datetime.fromtimestamp(timestamp / 1000.0)  # Make sure that UNIX timestamp is in (ms); converts it to datetime
    start_date, end_date = determine_timestamp_semester(timestamp)

    if start_date is None or end_date is None: # skip if timestamp is outside of semester; for debugging purposes mostly
        return None, None

    # get duration of semester time that has passed of it at timestamp
    semester_duration = (end_date - start_date).days
    time_passed = (timestamp - start_date).days

    # determine if timestamp is within first 3 weeks, last 3 weeks, or inbetween
    first_3_weeks = 21
    last_3_weeks = semester_duration - 21
    
    if time_passed <= first_3_weeks:
        quantile = Quantile.First_3_weeks
    elif time_passed >= last_3_weeks:
        quantile = Quantile.Last_3_weeks
    else:
        quantile = Quantile.Middle

    # calculate the quantile in percentage
    progress_percentage = time_passed / semester_duration
    

    return quantile, round(progress_percentage, 2)
