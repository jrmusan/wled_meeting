import requests
from datetime import datetime, timedelta
import urllib.parse
import json
import pytz
import asyncio
import pickle
import os
import time

import wled_controller


#~~~~~~~~~~~~~~CREDIT TO ALL THE FANCY GOOGLE MEET STUFF GOES TO @pbitutsky (https://paul.bitutsky.com/)~~~~~~~~~~~~~~

with open("cal_url.txt", 'r') as f:
    url = f.read()

GCALENDAR_URL_TEMPLATE = url
LOCAL_TIMEZONE = "America/New_York"  # Replace this with your time zone.
SMART_DEVICE_NAME = "NanoLeafs" # Replace this with your smart device name
LOCAL_CACHE_FILEPATH = "cache.pkl"

WORKDAY_START = "8:00AM"
WORKDAY_END = "4:00PM"

NANO_LEAF_URL = 'http://nanoleaf.local/json/state'
header = {'Content-Type': 'application/json'}

def get_busy_times_from_google_calendar():
    """Returns a list of tuples (start time, end time) that represent busy times."""

    # Headers for the HTTP GET request.
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Mobile Safari/537.36",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }

    # Define a function encode which will take a string as input and return a
    # URL-safe version. For example: "America/New_York" is converted to
    # "America%2FNew_York".
    encode = lambda string: urllib.parse.quote(string, safe="")

    # Get the time at the start of the current day (midnight) in this timezone.
    timezone = pytz.timezone(LOCAL_TIMEZONE)
    start_of_today = timezone.localize(datetime.now()).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    start_of_tomorrow = start_of_today + timedelta(days=1)

    # Generate the URL with the timezone, start date, and end date parameters.
    url = GCALENDAR_URL_TEMPLATE.format(
        timezone=encode(LOCAL_TIMEZONE),
        start_datetime=encode(start_of_today.isoformat()),
        end_datetime=encode(start_of_tomorrow.isoformat()),
    )

    # Send the request, get the response, parse it.
    response = requests.get(url, headers=headers)
    parsed_response = json.loads(response.text)

    # Get the start and end times from all of the events.
    busy_times = []
    for event in parsed_response["items"]:
        event_start = datetime.fromisoformat(event["start"]["dateTime"])
        event_end = datetime.fromisoformat(event["end"]["dateTime"])

        # Do not include all-day events.
        if event_end - event_start == timedelta(days=1):
            continue
        
        busy_times.append((event_start, event_end))

    return busy_times

def check_if_busy(busy_times, time_to_check):
    """Checks if I am busy at a given time. Returns True if busy, False if free."""
    return any(
        [start_time <= time_to_check <= end_time for start_time, end_time in busy_times]
    )

def set_device_state(request_on=False):
    """Turns the nano leafs on or off."""

    if request_on:
        print("Setting red")
        wled_controller.set_red()
    else:
        print("Setting green")
        wled_controller.set_green()

def main():
    # Get the current time.
    timezone = pytz.timezone(LOCAL_TIMEZONE)
    now = timezone.localize(datetime.now())

    # Don't read from cache if the minute is divisible by 5 (e.g. 6:00, 6:05)
    # or if the local cache does not exist
    # or if the local cache has not yet been modified today
    do_not_read_cache = (
        now.minute % 5 == 0
        or not os.path.exists(LOCAL_CACHE_FILEPATH)
        or timezone.localize(
            datetime.fromtimestamp(os.path.getmtime(LOCAL_CACHE_FILEPATH))
        ).date()
        != now.date()
    )

    if do_not_read_cache:
        # Get the busy times from Google Calendar.
        busy_times = get_busy_times_from_google_calendar()
    
    else:
        # Read the busy times
        cache = open(LOCAL_CACHE_FILEPATH, "rb")
        cached_data = pickle.load(cache)
        cache.close()
        busy_times = cached_data["busy_times"]

    # If we're outside of workday hours, do nothing except turn the plug off.
    workday_start_time = datetime.strptime(WORKDAY_START, "%I:%M%p").time()
    workday_end_time = datetime.strptime(WORKDAY_END, "%I:%M%p").time()
    if not (workday_start_time <= now.time() <= workday_end_time):
        set_device_state(False)
        return


    # Check if I'm busy right now and if so, turn the light on. Otherwise, turn it off
    busy_right_now = check_if_busy(busy_times, now)
    set_device_state(busy_right_now)

    # Create the cache if it does not exist.
    if not os.path.exists(LOCAL_CACHE_FILEPATH):
        open(LOCAL_CACHE_FILEPATH, "w+").close()

    # Write to the cache
    data_to_write = {"busy_times": busy_times}
    cache = open(LOCAL_CACHE_FILEPATH, "wb")
    pickle.dump(data_to_write, cache)
    cache.close()

if __name__ == "__main__":

    while True:
        main()
        time.sleep(60)
