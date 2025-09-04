from quart import Blueprint, render_template, render_template_string
from quart_auth import login_required, login_user, logout_user, Unauthorized, AuthUser, current_user
from ..db_interface import db_interface
from ..db_interface.user_model import User

bp = Blueprint('home_page', __name__, url_prefix="/")

# Import all related api files

# Register all related api blueprints

# All routes served under "/"

# this is the default index route; template served depends on website type + plugins chose; move this to home_page bp - bp can have same url_prefix if different names
@bp.route("")
@login_required
async def index():
    async with db_interface.create_session() as session:
        logged_in_user_info = await User.get_by_id(session, int(current_user.auth_id))

    return await render_template('index.html', logged_in_user_info=logged_in_user_info)

@bp.route("overview")
@login_required
async def overview():
    async with db_interface.create_session() as session:
        logged_in_user_info = await User.get_by_id(session, int(current_user.auth_id))

    return await render_template('overview.html', logged_in_user_info=logged_in_user_info)