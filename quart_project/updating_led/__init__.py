import quart
import requests
from quart_schema import validate_request
from quart_auth import login_required, current_user
from datetime import date

from ..db_interface.user_model import User
from ..db_interface.led_model import LED_Device
from ..db_interface.calendar_event_model import CalendarEvent
from ..db_interface import db_interface
from . import schemas

bp = quart.Blueprint('updating_led', __name__, url_prefix="/led")

# convert DB format to hex (frontend)
def rgb_to_hex(rgb_str: str) -> str:
    # input format: "(0, 0, 255)" or "0, 0, 255"
    nums = [int(x) for x in rgb_str.strip("() ").split(",")]
    return "#{:02x}{:02x}{:02x}".format(*nums)

# convert hex (frontend) to DB format
def hex_to_rgb(hex_str: str) -> str:
    hex_str = hex_str.lstrip("#")
    r, g, b = tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))
    return f"({r}, {g}, {b})"

# white listed pi-led IPs
white_listed_ips = ["192.168.8.23", "192.168.8.24"]

# Route which pis use to get the current info for them to display (called on pi boot)
@bp.get("pi_info/<string:pi_name>")
async def pi_info(pi_name: str):
    # if not a pi abort unauthorized request
    client_ip = quart.request.remote_addr
    if client_ip not in white_listed_ips:
        quart.abort(403)

    # otherwise get the value held in the DB for this pi and return it
    async with db_interface.create_session() as session:
        pi_info = await LED_Device.get_device_by_name(session, pi_name)
        if pi_info:
            today = date.today()
            today_events = await CalendarEvent.get_al_events_for_day(session, today.day, today.month, today.year)
            events = [{
                "time": f"{obj.hour}:{obj.minute}",  # zero-padded
                "title": obj.title
            } for obj in today_events ]
            return { "message": pi_info.message, "color": pi_info.color, "wrap_text": pi_info.text_wrap, "display_type": pi_info.display_type, "events": events }
        else:
            return { "error_msg": "pi not found - defaulting to clock mode; check the Username of the Pi and the Central DB values"}

# Route which returns the html form needed to update the message, color, wrap, and who to send to fields
@bp.get("update_message")
@login_required
async def update_message():
    # get all of the LED pis currently stored in the db to return them
    async with db_interface.create_session() as session:
        all_pi_info = await LED_Device.get_all(session)
        front_end_pi_info = []
        # convert the DB values into Jinja compatible values
        for row in all_pi_info:
            row = row.to_dict()
            row['color'] = rgb_to_hex(row['color'])
            front_end_pi_info.append(row)

        logged_in_user_info = await User.get_by_id(session, int(current_user.auth_id))
        return await quart.render_template('update_message.html', all_pi_info=front_end_pi_info, logged_in_user_info=logged_in_user_info)

# receives POST request from a user which will update the given pi
@bp.post("update_message")
@login_required
@validate_request(schemas.UpdateLedScreen)
async def update_message_form(data: schemas.UpdateLedScreen):
    async with db_interface.create_session() as session:
        # get the unique name of the pi requested
        led_device = await LED_Device.get_device_by_name(session, data.pi_name)
        led_device.message = data.message
        led_device.text_wrap = data.wrap_text
        led_device.color = hex_to_rgb(data.color)
        # store the new led info in the DB
        await LED_Device.edit(session, led_device)

        # if led_device display is message then hit the Pi webserver immediately with the update
        if led_device.display_type == "message":
            url = f"http://{led_device.ip_address}:{led_device.port}/update_message"
            payload = {
                'display_type': 'message',
                'message': data.message,
                'color': hex_to_rgb(data.color),
                'wrap_text': data.wrap_text
            }

            try: 
                resp = requests.post(url, json=payload)
                # log whether or not POST was successful
                if resp.status_code == 200:
                    print("Updated LED Device successfully")
                else:
                    print("Failed to update LED Device")
            except Exception as e:
                print(f"Exception when making request to external pi {url}, {payload}: ", e)
    
    # for now return redirect to home page eventually show upodated info
    return quart.redirect(quart.url_for('home_page.index'))

# Route which returns the html form needed to change the led display (clock, weather, message, calendar)
@bp.get("change_display")
@login_required
async def change_display():
    # get all of the LED pis currently stored in the db to return them
    async with db_interface.create_session() as session:
        logged_in_user_info = await User.get_by_id(session, int(current_user.auth_id))
        your_led_device = await LED_Device.get_device_by_name(session, logged_in_user_info.username)
        
        # convert the DB values into Jinja compatible values
        your_led_device = your_led_device.to_dict()
        your_led_device['color'] = rgb_to_hex(your_led_device['color'])
        return await quart.render_template('change_display.html', your_led_device=your_led_device, logged_in_user_info=logged_in_user_info)

# receives POST request from a user which will change the display of their given pi
@bp.post("change_display")
@login_required
@validate_request(schemas.ChangeDisplay)
async def change_display_form(data: schemas.ChangeDisplay):
    async with db_interface.create_session() as session:
        # get the unique name of the pi requested
        led_device = await LED_Device.get_device_by_name(session, data.pi_name)
        led_device.text_wrap = data.wrap_text
        led_device.display_type = data.display_type
        led_device.color = hex_to_rgb(data.color)
        # store the new led info in the DB
        await LED_Device.edit(session, led_device)

        # if led_device display is message then get message linked with the pi and show it on the screen
        url = f"http://{led_device.ip_address}:{led_device.port}/update_message"
        if led_device.display_type == "message":
            payload = {
                'display_type': 'message',
                'message': led_device.message,
                'color': led_device.color,
                'wrap_text': led_device.text_wrap
            }
        
        # else if display type is calendar then get the calendar events for current day and show them on the screen
        elif led_device.display_type == "calendar":
            today = date.today()
            today_events = await CalendarEvent.get_al_events_for_day(session, today.day, today.month, today.year)
            events = [{
                "time": f"{obj.hour}:{obj.minute}",  # zero-padded
                "title": obj.title
            } for obj in today_events ]
            payload = {
                'display_type': 'calendar',
                'events': events,
                'color': led_device.color,
                'wrap_text': led_device.text_wrap
            }

        # else if display type is clock simply send the clock request display
        elif led_device.display_type == "clock":
            payload = {
                'display_type': 'clock',
                'color': led_device.color,
                'wrap_text': led_device.text_wrap
            }

        # else if display type is weather simply send the weather request display
        elif led_device.display_type == "weather":
            payload = {
                'display_type': 'weather',
                'color': led_device.color,
                'wrap_text': led_device.text_wrap
            }
        
        # send the Request down to the pi immediately
        try: 
            resp = requests.post(url, json=payload)
            # log whether or not POST was successful
            if resp.status_code == 200:
                print("Updated LED Device successfully")
            else:
                print("Failed to update LED Device")

        except Exception as e:
            print(f"Exception when making request to external pi {url}, {payload}: ", e)
    
    # for now return redirect to home page eventually show upodated info
    return quart.redirect(quart.url_for('home_page.index'))