import threading
import requests
import time
import ast
import itertools

from zoneinfo import ZoneInfo
from datetime import datetime, date
from quart import Quart, jsonify, request
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics

import led_utils

app = Quart(__name__)
app.config["QUART_SCHEMA_CONVERT_CASING"] = True
app.config["QUART_SCHEMA_CONVERSION_PREFERENCE"] = "snake"

# ======== CONFIG (unique per Pi) ========
PI_NAME     = "nathan"                                          # change per device
CENTRAL_WS  = "http://192.168.8.21:8000/led/pi_info/" + PI_NAME # server URL to ping on boot
# =======================================

# ======== GLOBAL TRACKER (tells Pi what to display - message, weather, calendar, clock) ======== [message, color, wrap_text]
DISPLAY_COLOR = (0, 0, 255)
STORED_CAL_EVENTS = []
# =======================================

# ======== CONFIGURE LED MATRIX ONE TIME (height, width)========
text_font_path: str = "../rpi-rgb-led-matrix/fonts/5x7.bdf"
title_font_path: str = "../rpi-rgb-led-matrix/fonts/6x9.bdf"

# Configure LED matrix
options = RGBMatrixOptions()
options.rows = 32
options.cols = 64
options.chain_length = 1
options.parallel = 1
options.hardware_mapping = "regular"
options.led_rgb_sequence = "RBG" # idk why it needs this feels like it is flipping it but this hack works
matrix = RGBMatrix(options=options)
offscreen_canvas = matrix.CreateFrameCanvas()

# Load font
text_font = graphics.Font()
text_font.LoadFont(text_font_path)

title_font = graphics.Font()
title_font.LoadFont(title_font_path)
# =======================================

# ======== UTILITY FUNCTIONS ============
def get_weather_open_meteo():
    global offscreen_canvas, DISPLAY_COLOR
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

    resp = requests.get(url, params=params, verify="/etc/ssl/certs/ca-certificates.crt")
    resp.raise_for_status()
    data = resp.json()

    # Extract condition: Open-Meteo uses “weathercode” rather than descriptive string
    # So you’ll need to map weathercode to something like “Sunny”, “Rain”, etc.
    weather_code = data["current_weather"]["weathercode"]
    current_temp = data["current_weather"]["temperature"]

    # Daily low/high from “daily” field; index 0 corresponds to today
    temp_min = data["daily"]["temperature_2m_min"][0]
    temp_max = data["daily"]["temperature_2m_max"][0]

    # Map codes to description - must be 9 chars for LED display OR LESS - then padded with spaces just to make my life easy
    code_map = {
        0: "All Clear",
        1: "Clear Sky",
        2: "Pt Cloudy", # partly cloudy
        3: "Overcast ",
        45: "Fog   :) ",
        51: "Drizzle 1", # light, medium, heavy - must abbr down to 9 chars
        53: "Drizzle 2",
        55: "Drizzle 3",
        61: "Some Rain",
        63: "Med Rain ",
        65: "Hard Rain",
        71: "Snow  :) ",
        80: "Showering",
        # Add more as needed
    }
    condition = code_map.get(weather_code, f"Code {weather_code}")

    # Round temps if you like
    curr = round(current_temp)
    low = round(temp_min)
    high = round(temp_max)
    weather_line_1 = f"{curr} {condition}"
    weather_line_2 = f"Hi {high}/Lo {low}"
    lines = [gen_date_title(), weather_line_1, weather_line_2]
    offscreen_canvas = led_utils.display_text(matrix, offscreen_canvas, text_font, title_font, lines=lines, hasTitle=True, color=DISPLAY_COLOR)

# helper function to generate the title: mm/dd/yyyy
def gen_date_title():
    today = date.today()
    day = today.day
    month = today.month
    year = today.year
    return f"{month}/{day}/{year}"

# 45 chars max if msg[11], msg[23], msg[35] is not a SPACE then add a "-" to string
def format_custom_msg(message):
    formatted = [message]
    if len(message) > 12: 
        if message[12] != " ":
            message = message[:12] + "-" + message[12:]
        formatted = [message[:12], message[12:]]

    if len(message) > 24:
        if message[24] != " ":
            message = message[:24] + "-" + message[24:]
        formatted = [message[:12], message[12:24], message[24:]]

    if len(message) > 36:
        if message[36] != " ":
            message = message[:36] + "-" + message[36:]
        formatted = [message[:12], message[12:24], message[24:36], message[36:]]

    return formatted

# =============================================


# ==========   DISPLAY FUNCTIONS    ===========

# continuously show the weather every 15 minutes
def display_weather(stop_event):
    while not stop_event.is_set():
        try:
            get_weather_open_meteo()
        except KeyboardInterrupt:
            print("\nClock stopped.")
            break

        # Poll for weather every 15 minutes but check if flag set every second
        for i in range(900):
            time.sleep(1)
            # if set breaks out and then will leave next while iter
            if stop_event.is_set():
                break

# have a running clock updated every second for NY timezone
def display_clock(stop_event, timezone="America/New_York"):
    global offscreen_canvas, DISPLAY_COLOR
    # will check every sec to see if need to break
    while not stop_event.is_set():
        try:
            now = datetime.now(ZoneInfo(timezone))
            clock_str = now.strftime("%H:%M:%S")
            lines = [gen_date_title(), clock_str]
            offscreen_canvas = led_utils.display_text(matrix, offscreen_canvas, text_font, title_font, lines=lines, hasTitle=True, color=DISPLAY_COLOR, title_gap=15)
            time.sleep(1)
        except KeyboardInterrupt:
            print("\nClock stopped.")
            break

# display calendar events one at a time
def display_calendar_events(stop_event):
    global offscreen_canvas, DISPLAY_COLOR, STORED_CAL_EVENTS
    # cycle over stored calendar
    if STORED_CAL_EVENTS == []:
        lines = [gen_date_title(), f"No Events"]
        offscreen_canvas = led_utils.display_text(matrix, offscreen_canvas, text_font, title_font, lines=lines, hasTitle=True, color=DISPLAY_COLOR)
        # busy work until it changes
        while not stop_event.is_set():
            time.sleep(1)

    else:
        for event in itertools.cycle(STORED_CAL_EVENTS):
            if stop_event.is_set():
                break
            try:
                lines = [gen_date_title(), f"Time: {event[0]}", event[1]] # title limit to 12 chars
                offscreen_canvas = led_utils.display_text(matrix, offscreen_canvas, text_font, title_font, lines=lines, hasTitle=True, color=DISPLAY_COLOR)
                # Update cal event every 15 sec but check if flag set every second
                for i in range(15):
                    time.sleep(1)
                    # if set breaks out and then will leave next while iter
                    if stop_event.is_set():
                        break
                led_utils.clear_canvas(matrix)
                time.sleep(1)
            except KeyboardInterrupt:
                print("\nCal Event Stopped.")
                break

# show formatted msg
def display_msg(stop_event, msg):
    global offscreen_canvas, DISPLAY_COLOR
    # display msg one time then hold until mode is changed
    print(DISPLAY_COLOR)
    offscreen_canvas = led_utils.display_text(matrix, offscreen_canvas, text_font, title_font, format_custom_msg(msg), color=DISPLAY_COLOR)
    # busy work until it changes
    while not stop_event.is_set():
        time.sleep(1)

# =======================================


# ======== BG THREADING DISPLAY ========

# Shared state
current_display_type = {"display_type": "clock"}  # default mode
display_type_lock = threading.Lock()
stop_event = threading.Event()

def display_worker():
    global DISPLAY_COLOR, STORED_CAL_EVENTS, display_type_lock
    """Runs forever, switching between modes when current_display_type changes."""
    while True:
        stop_event.clear()
        with display_type_lock:
            display_type = current_display_type["display_type"]

            message = current_display_type.get("message", "Default Message")
            DISPLAY_COLOR = ast.literal_eval(current_display_type.get("color", "(0, 0, 255)"))
            STORED_CAL_EVENTS = []
            if current_display_type.get("events"):
                for event in current_display_type.get("events", []):
                    STORED_CAL_EVENTS.append([event["time"], event["title"]])
        
        print(f"Choosing next mode... {display_type}")
        if display_type == "clock":
            display_clock(stop_event)
        elif display_type == "weather":
            display_weather(stop_event)
        elif display_type == "message":
            display_msg(stop_event, message)
        elif display_type == "calendar":
            display_calendar_events(stop_event)
        else: # default clock
            display_clock(stop_event)

worker_thread = threading.Thread(target=display_worker, daemon=True)
worker_thread.start()
# =======================================


# ======    WEB C&C SERVER CODE   ========
@app.post("/update_message")
async def update_message():
    data = await request.get_json()
    handle_web_data(data)
    return jsonify( {"status": "updated_screen"} )

# Upon app startup make a request to the DB so it knows what to display on the LED panel (default is clock in DB)
@app.before_serving
async def before_serving():
    # on boot reach out to the central server to get the updated info for the pi
    response = requests.get(CENTRAL_WS)
    # if successful then display
    if response.status_code == 200:
        data = response.json()
        handle_web_data(data)

def handle_web_data(data):
    global display_type_lock
    display_type = data.get("display_type")
    message = data.get("message")
    color = data.get("color")
    events = data.get("events")
    print(f"New Request: [Display Type: {display_type}, Message: {message}, Color: {color}, Events: {events}]")

    with display_type_lock:
        current_display_type["display_type"] = display_type
        current_display_type["events"] = events

        if message:
            current_display_type["message"] = message
        if color:
            current_display_type["color"] = color
    
    stop_event.set()  # tells current loop to stop, worker will restart next mode

# =======================================