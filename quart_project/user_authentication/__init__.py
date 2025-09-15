import quart
from quart import redirect, url_for
from quart_schema import validate_request
from quart_auth import login_required, login_user, logout_user, AuthUser, current_user

from ..db_interface.user_model import User
from ..db_interface import db_interface
from . import schemas
from . import auth_utils

bp = quart.Blueprint('authentication', __name__, url_prefix="/")


# reset_password route for a user to reset password form
@bp.get("reset_password")
@login_required
async def reset_password():
    async with db_interface.create_session() as session:
        logged_in_user_info = await User.get_by_id(session, int(current_user.auth_id))

    return await quart.render_template('reset_password.html', logged_in_user_info=logged_in_user_info)

# profile route for a user to edit all their info; reset password; toggle dark mode; etc
@bp.get("profile")
@login_required
async def profile():
    async with db_interface.create_session() as session:
        logged_in_user_info = await User.get_by_id(session, int(current_user.auth_id))

    return await quart.render_template('profile.html', logged_in_user_info=logged_in_user_info)

# receives POST request from the user asking to change their password
@bp.post("reset_password")
@login_required
@validate_request(schemas.ResetPassword)
async def reset_password_form(data: schemas.ResetPassword):
    async with db_interface.create_session() as session:
        # check if the user exists
        user = await User.get_user_by_username(session, data.username)
        # verify that passwords match
        if data.password == data.password_verify:
            print("Changing password for ", user.username)
            hashed_pwd = auth_utils.hash_password(data.password)
            user.hashed_password = hashed_pwd
            await User.edit(session, user)
            return redirect(url_for('home_page.index'))
        else:
            print("Password do not match")
            return redirect(url_for('authentication.profile'))

# receives POST request from the user asking to change their information
@bp.post("apply_changes")
@login_required
@validate_request(schemas.ApplyChanges)
async def apply_changes(data: schemas.ApplyChanges):
    async with db_interface.create_session() as session:
        # check if the user exists
        logged_in_user_info = await User.get_by_id(session, int(current_user.auth_id))
        # verify that all fields changed are unique
        if await User.get_user_by_email(session, data.email) is not None:
            return {"error": f"Email {data.email} already exists"}
        if await User.get_user_by_username(session, data.username) is not None:
            return {"error": f"Username {data.username} already exists"}
        if await User.get_user_by_phone_number(session, data.phone_number) is not None:
            return {"error": f"Phone Number {data.phone_number} already exists"}
        
        # if makes it here then a valid change
        logged_in_user_info.phone_number = data.phone_number
        logged_in_user_info.email = data.email
        logged_in_user_info.username = data.username
        await User.edit(session, logged_in_user_info)
        return redirect(url_for('authentication.profile'))
    
# receives POST request from the user asking to change their colors for their events
@bp.post("color_changes")
@login_required
@validate_request(schemas.ColorChanges)
async def color_changes(data: schemas.ColorChanges):
    async with db_interface.create_session() as session:
        # check if the user exists
        logged_in_user_info = await User.get_by_id(session, int(current_user.auth_id))
        
        # if makes it here then a valid change
        logged_in_user_info.cal_event_color = data.cal_event_color
        logged_in_user_info.todo_event_color = data.todo_event_color

        await User.edit(session, logged_in_user_info)
        return redirect(url_for('authentication.profile'))

# serve the login form
@bp.get("login")
async def login_form():
    return await quart.render_template('login.html')

# receives POST request when the user signs up; checks that no other user with that email exists - hashes password and adds it into DB
# validates the incoming request with pydantic; data will hold the validated json request params
@bp.post("login")
@validate_request(schemas.UserLogin)
async def process_login(data: schemas.UserLogin):
    async with db_interface.create_session() as session:
        # check if the user exists
        user = await User.get_user_by_username(session, data.username)
        # verify that the password matches the hashed password
        if user and auth_utils.verify_password(data.password, user.hashed_password):
            login_user(AuthUser(str(user.id)))  # quart uses string as AuthUser - access ID via current_user.auth_id, current_user.is_authenticated bool for logged in or out user
            print("Successful login for ", data.username)
            return redirect(url_for('home_page.index'))
        else:
            print("Unsuccessful login for ", data.username)
            return {"error": "Invalid Credentials"}
        
@bp.get("logout")
async def process_logout():
    logout_user()
    return redirect(url_for('home_page.index'))