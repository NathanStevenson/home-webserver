import quart
from datetime import date
import requests
from quart_schema import validate_request
from quart_auth import login_required, current_user

from ..db_interface.user_model import User
from ..db_interface.calendar_event_model import CalendarEvent
from ..db_interface.led_model import LED_Device
from ..db_interface import db_interface
from . import schemas

bp = quart.Blueprint('calendar', __name__, url_prefix="/calendar")

# Route which returns the html form for the calendar
@bp.get("")
@login_required
async def calendar():
    # get all of the calendar events to send to the frontend
    async with db_interface.create_session() as session:
        all_calendar_events = await CalendarEvent.get_all_with_users(session)
        front_end_calendar_info = []
        # convert the DB values into Jinja compatible values
        for row in all_calendar_events:
            row = row.to_dict(include_related={"user": ["cal_event_color"]})
            front_end_calendar_info.append(row)

        logged_in_user_info = await User.get_by_id(session, int(current_user.auth_id))
        return await quart.render_template('calendar.html', all_calendar_events=front_end_calendar_info, logged_in_user_info=logged_in_user_info)

# utility function to update the LED device calendar display after adding, editing, or deleting
async def update_cal_leds(all_cal_leds, day, month, year):
    async with db_interface.create_session() as session:
        today_events = await CalendarEvent.get_al_events_for_day(session, day, month, year)
        events = [{
            "time": f"{obj.hour}:{obj.minute}",  # zero-padded
            "title": obj.title
        } for obj in today_events ]
        print("FIND THIS SHIT", events, day, all_cal_leds)
        for device in all_cal_leds:
            url = f"http://{device.ip_address}:{device.port}/update_message"
            payload = {
                'display_type': 'calendar',
                'events': events,
            }
            resp = requests.post(url, json=payload)
            # log whether or not POST was successful
            if resp.status_code == 200:
                print("Updated LED Device successfully")
            else:
                print("Failed to update LED Device")


# receives POST request from a user which will add a calendar event to db
@bp.post("event")
@login_required
@validate_request(schemas.CalendarEvent)
async def add_event_form(data: schemas.CalendarEvent):
    async with db_interface.create_session() as session:
        calendar_event = CalendarEvent(data.minute, data.hour, data.day, data.month, data.year, data.title, data.description, int(current_user.auth_id))
        await CalendarEvent.add(session, calendar_event)

        # any time a calendar event is added, edited, or deleted ON TODAYS DATE get all the LEDs who are currently showing the Calendar Events and hit their Update Message URL with all Cal Events for current day
        all_cal_leds = await LED_Device.get_all_calendar_devices(session)
        today = date.today()
        print("FIND THIS SHIT 21", today, data.day, data.month, data.year, all_cal_leds)
        if all_cal_leds != [] and str(today.day) == data.day and str(today.month) == data.month and str(today.year) == data.year:
            await update_cal_leds(all_cal_leds, data.day, data.month, data.year)

        # redirect user back to calendar page will now show the new event
        return quart.redirect(quart.url_for('calendar.calendar'))
    return {"error": "Failed to add event to database"}

# receives PATCH request from a user which will edit a calendar event to db - will have the id field hidden on form
@bp.patch("event")
@login_required
@validate_request(schemas.CalendarEvent)
async def update_event_form(data: schemas.CalendarEvent):
    async with db_interface.create_session() as session:
        calendar_event = await CalendarEvent.get_by_id(session, data.id)
        calendar_event.minute = data.minute
        calendar_event.hour = data.hour
        calendar_event.title = data.title
        calendar_event.description = data.description
        await CalendarEvent.edit(session, calendar_event)

        # any time a calendar event is added, edited, or deleted ON TODAYS DATE get all the LEDs who are currently showing the Calendar Events and hit their Update Message URL with all Cal Events for current day
        all_cal_leds = await LED_Device.get_all_calendar_devices(session)
        today = date.today()
        if all_cal_leds != [] and str(today.day) == data.day and str(today.month) == data.month and str(today.year) == data.year:
            await update_cal_leds(all_cal_leds, data.day, data.month, data.year)

        # for now return redirect to home page eventually show upodated info
        return quart.redirect(quart.url_for('calendar.calendar'))
    return {"error": "Failed to update event in database"}

# receives POST request from a user which will delete a calendar event to db - will have the id field hidden on form
@bp.delete("event/<int:id>")
@login_required
async def delete_event_form(id: int):
    async with db_interface.create_session() as session:
        update_led_flag = False
        # if deleting event on same day as today have to update the leds POST delete
        today = date.today()
        calendar_event = await CalendarEvent.get_by_id(session, id)
        if calendar_event and calendar_event.day == str(today.day) and calendar_event.month == str(today.month) and calendar_event.year == str(today.year):
            update_led_flag = True
        await CalendarEvent.delete(session, calendar_event)

        # any time a calendar event is added, edited, or deleted ON TODAYS DATE get all the LEDs who are currently showing the Calendar Events and hit their Update Message URL with all Cal Events for current day
        if update_led_flag:
            all_cal_leds = await LED_Device.get_all_calendar_devices(session)
            await update_cal_leds(all_cal_leds, today.day, today.month, today.year)

        # for now return redirect to home page eventually show upodated info
        return quart.redirect(quart.url_for('calendar.calendar'))
    return {"error": "Failed to delete event in database"}