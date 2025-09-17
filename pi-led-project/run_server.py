import uvicorn
import requests
import json
import time
import pytz
import itertools

from datetime import datetime, date
from quart import Quart, jsonify
from quart_schema import validate_request

import led_utils
import schemas

app = Quart(__name__)
app.config["QUART_SCHEMA_CONVERT_CASING"] = True
app.config["QUART_SCHEMA_CONVERSION_PREFERENCE"] = "snake"

# ======== CONFIG (unique per Pi) ========
PI_NAME     = "nathan"                                          # change per device
CENTRAL_WS  = "http://192.168.8.21:8000/led/pi_info/" + PI_NAME # server URL to ping on boot
# =======================================

# ======== GLOBAL TRACKER (tells Pi what to display - message, weather, calendar, clock) ======== [message, color, wrap_text]
DISPLAY_COLOR = "(0, 0, 255)"
DISPLAY_TYPE = 'message'
STORED_MESSAGE = []
STORED_CAL_EVENTS = [["10:30", "Event 1"], ["13:35", "Event 2"]] # trial test data
# =======================================

# ======== HELPER FUNCTIONS (displaying clock, and weather)
def get_weather_open_meteo():
    """
    Get weather from Open-Meteo and print:
      <Condition> <CurrentTemp> <LowTemp>/<HighTemp>
    """

    # Query parameters: current weather, daily temp min/max
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": "38.968059",
        "longitude": "-77.360431",
        "current_weather": True,
        "daily": "temperature_2m_min,temperature_2m_max",
        "temperature_unit": "fahrenheit",
        "timezone": "auto"  # or you can specify e.g. "America/New_York"
    }

    resp = requests.get(url, params=params)
    resp.raise_for_status()
    data = resp.json()

    # Extract condition: Open-Meteo uses “weathercode” rather than descriptive string
    # So you’ll need to map weathercode to something like “Sunny”, “Rain”, etc.
    weather_code = data["current_weather"]["weathercode"]
    current_temp = data["current_weather"]["temperature"]

    # Daily low/high from “daily” field; index 0 corresponds to today
    temp_min = data["daily"]["temperature_2m_min"][0]
    temp_max = data["daily"]["temperature_2m_max"][0]

    # Map codes to description (simple version)
    code_map = {
        0: "Clear",
        1: "Mainly Clear",
        2: "Partly Cloudy",
        3: "Overcast",
        45: "Fog",
        51: "Light Drizzle",
        53: "Moderate Drizzle",
        55: "Dense Drizzle",
        61: "Light Rain",
        63: "Moderate Rain",
        65: "Heavy Rain",
        71: "Snow",
        80: "Rain Showers",
        # Add more as needed
    }
    condition = code_map.get(weather_code, f"Code {weather_code}")

    # Round temps if you like
    curr = round(current_temp)
    low = round(temp_min)
    high = round(temp_max)

    weather_message = f"{curr} {condition}   {low}/{high}"
    # led_utils.display_text(data.pi_message, color=data.pi_color, wrap=data.pi_wrap)
    print(f'Displaying message to LED: {weather_message} {DISPLAY_COLOR} {True}')

# continuously show the weather every 15 minutes
def poll_weather():
    while True:
        try:
            get_weather_open_meteo()
        except Exception as e:
            print("Error getting weather:", e)

        # Wait 15 minutes
        time.sleep(900)

# have a running clock updated every second for NY timezone
def run_clock(timezone="America/New_York"):
    tz = pytz.timezone(timezone)
    while True:
        try:
            now = datetime.now(tz)
            # led_utils.display_text(data.message, color=data.color, wrap=data.wrapText)
            clock_str = now.strftime("%H:%M:%S")
            print(f"\r{clock_str}", end="", flush=True)  # overwrite line
            time.sleep(1)
        except KeyboardInterrupt:
            print("\nClock stopped.")

# display calendar events one at a time
def display_calendar_events():
    # get current day info
    today = date.today()
    day = today.day
    month = today.month
    year = today.year
    title = f"{month}/{day}/{year}"
    # led_utils.display_text(data.message, color=data.color, wrap=data.wrapText)
    print(title)
    # cycle over stored calendar
    for event in itertools.cycle(STORED_CAL_EVENTS):
        # led_utils.display_text(data.message, color=data.color, wrap=data.wrapText)
        print(f"\r{event[0]}: {event[1]}", end="", flush=True)
        time.sleep(5)
        # clear_canvas()
        print("\r", end="", flush=True) # clearing the space
        time.sleep(1)

# =======================================

# Flexible endpoint to update LED screen; can change color; text-wrap; or display type; if message/calendar will also contain the DB data currently on the server
@app.post("/update_message")
@validate_request(schemas.UpdateLedScreen)
async def update_message(data: schemas.UpdateLedScreen):
    # led_utils.display_text(data.message, color=data.color, wrap=data.wrapText)
    print(f"Displaying message to LED: {data.message} {data.color} {data.wrap_text}")
    return jsonify( {"status": "updated_screen"} )

if __name__ == "__main__":
    # on boot reach out to the central server to get the updated info for the pi
    response = requests.get(CENTRAL_WS)
    # if successful then display
    if response.status_code == 200:
        data = response.json()
        if data['pi_display_type'] and data['color']:
            DISPLAY_TYPE = data['pi_display_type']
            DISPLAY_COLOR = data['color']
        # if display message then display current msg stored in db
        if (DISPLAY_TYPE == 'message'):
            STORED_MESSAGE = [data["pi_message"], data["pi_color"], data["pi_wrap"]]
            # led_utils.display_text(data.pi_message, color=data.pi_color, wrap=data.pi_wrap)
            print(f'Displaying message to LED: {STORED_MESSAGE[0]} {STORED_MESSAGE[1]} {STORED_MESSAGE[2]}')\
        
        # if display weather then continuously poll Open-Meteo every 15minutes for weather updates
        if (DISPLAY_TYPE == 'weather'):
            poll_weather()
        
        # if display clock then print an updating clock to the screen (every second - rpi matrix can handle 30FPS refresh)
        if (DISPLAY_TYPE == 'clock'):
            run_clock()

        # if display calendar then print the events for the day; print DATE /n [Cal_Event[0], clear screen for 1 second, Cal_Event[1], loop...] - show for 5s clear for 1s
        if (DISPLAY_TYPE == 'calendar'):
            for event in data["cal_events"]:
                STORED_CAL_EVENTS.append(event['time'], event['title'])
            display_calendar_events()       

    # Run the tiny control server that central will call
    uvicorn.run("run_server:app", host="0.0.0.0", port=8000, timeout_graceful_shutdown=3)
