import quart
from quart import redirect, url_for
from quart_schema import validate_request
from quart_auth import login_required, login_user, logout_user, Unauthorized, AuthUser, current_user

from ..db_interface.user_model import User
from ..db_interface import db_interface
from . import schemas
from . import auth_utils

bp = quart.Blueprint('authentication', __name__, url_prefix="/")


# private route which serves /private HTML template; default tab shown on the web - only accessed with successful login
@bp.get("private")
@login_required
async def private_route():
    tabs = ["Overview"]
    if await current_user.is_authenticated:
        control_tabs = ["Logout", "Dark Mode"]
    else:
        control_tabs = ["Login", "Dark Mode"]

    async with db_interface.create_session() as session:
        logged_in_user_info = await User.get_by_id(session, int(current_user.auth_id))
    return await quart.render_template('private.html', tabs=tabs, control_tabs=control_tabs, logged_in_user_info=logged_in_user_info)

# if you fail a login requirement instead of default 401 unauthorized serve this custom 
@bp.errorhandler(Unauthorized)
async def custom_unauthorized_page(error):
    tabs = ["Overview"]
    if await current_user.is_authenticated:
        control_tabs = ["Logout", "Dark Mode"]
    else:
        control_tabs = ["Login", "Dark Mode"]
    return await quart.render_template('unauthorized.html', tabs=tabs, control_tabs=control_tabs)

# serve the login form
@bp.get("login")
async def login_form():
    tabs = ["Overview"]
    if await current_user.is_authenticated:
        control_tabs = ["Logout", "Dark Mode"]
    else:
        control_tabs = ["Login", "Dark Mode"]
    return await quart.render_template('login.html', tabs=tabs, control_tabs=control_tabs)

# receives POST request when the user signs up; checks that no other user with that email exists - hashes password and adds it into DB
# validates the incoming request with pydantic; data will hold the validated json request params
@bp.post("login")
@validate_request(schemas.UserLogin)
async def process_login(data: schemas.UserLogin):
    async with db_interface.create_session() as session:
        # check if the user exists
        user = await User.get_user_by_email(session, data.email)
        # verify that the password matches the hashed password
        if user and auth_utils.verify_password(data.password, user.hashed_password):
            login_user(AuthUser(str(user.id)))  # quart uses string as AuthUser - access ID via current_user.auth_id, current_user.is_authenticated bool for logged in or out user
            print("Successful login for ", data.email)
            return redirect(url_for('authentication.private_route'))
        else:
            print("Unsuccessful login for ", data.email)
            return {"error_msg": "Unsuccessful login!"}
        
@bp.get("logout")
async def process_logout():
    logout_user()
    return redirect(url_for('html_routes.index'))