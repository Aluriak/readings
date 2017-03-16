import time

def last_hours(n:int):  return time.time() - 3600 * n
def last_days(n:int):  return time.time() - 3600 * 24 * n
def last_weeks(n:int):  return time.time() - 3600 * 24 * 7 * n

last_hour = last_hours(1)
today = last_days(1)
this_week = last_weeks(1)
