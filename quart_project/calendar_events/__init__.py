import quart
import requests
from quart_schema import validate_request
from quart_auth import login_required, current_user

from ..db_interface.user_model import User
from ..db_interface.calendar_event_model import CalendarEvent
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

# receives POST request from a user which will add a calendar event to db
@bp.post("event")
@login_required
@validate_request(schemas.CalendarEvent)
async def add_event_form(data: schemas.CalendarEvent):
    async with db_interface.create_session() as session:
        calendar_event = CalendarEvent(data.day, data.month, data.year, data.title, data.description, int(current_user.auth_id))
        await CalendarEvent.add(session, calendar_event)
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
        calendar_event.title = data.title
        calendar_event.description = data.description
        await CalendarEvent.edit(session, calendar_event)
        # for now return redirect to home page eventually show upodated info
        return quart.redirect(quart.url_for('calendar.calendar'))
    return {"error": "Failed to update event in database"}

# receives POST request from a user which will delete a calendar event to db - will have the id field hidden on form
@bp.delete("event/<int:id>")
@login_required
async def delete_event_form(id: int):
    async with db_interface.create_session() as session:
        calendar_event = await CalendarEvent.get_by_id(session, id)
        await CalendarEvent.delete(session, calendar_event)
        # for now return redirect to home page eventually show upodated info
        return quart.redirect(quart.url_for('calendar.calendar'))
    return {"error": "Failed to delete event in database"}