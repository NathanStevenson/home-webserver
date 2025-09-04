import quart
from quart import redirect, url_for
from quart_schema import validate_request
from quart_auth import login_required, login_user, logout_user, AuthUser, current_user

from ..db_interface.user_model import User
from ..db_interface import db_interface
from . import schemas
from . import auth_utils

bp = quart.Blueprint('authentication', __name__, url_prefix="/")


# profile route for a user to see and edit basic information about themselves
@bp.get("profile")
@login_required
async def profile():
    async with db_interface.create_session() as session:
        logged_in_user_info = await User.get_by_id(session, int(current_user.auth_id))

    return await quart.render_template('profile.html', logged_in_user_info=logged_in_user_info)

# receives POST request from the user asking to change their password
@bp.post("reset_password")
@validate_request(schemas.ResetPassword)
async def reset_password(data: schemas.ResetPassword):
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
            return {"error_msg": "Unsuccessful login!"}
        
@bp.get("logout")
async def process_logout():
    logout_user()
    return redirect(url_for('home_page.index'))