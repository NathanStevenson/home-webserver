from quart import Blueprint, render_template, render_template_string
from quart_auth import current_user

bp = Blueprint('html_routes', __name__, url_prefix="/")

# Import all related api files

# Register all related api blueprints

# All routes served under "/"

# this is the default index route; template served depends on website type + plugins chose; move this to html_routes bp - bp can have same url_prefix if different names
@bp.route("")
async def index():
    tabs = ["Overview"]
    if await current_user.is_authenticated:
        control_tabs = ["Logout", "Dark Mode"]
    else:
        control_tabs = ["Login", "Dark Mode"]
    return await render_template('index.html', backend="quart_project", frontend="jinja", database="postgresql", tabs=tabs, control_tabs=control_tabs)

@bp.route("overview")
async def overview():
    tabs = ["Overview"]
    if await current_user.is_authenticated:
        control_tabs = ["Logout", "Dark Mode"]
    else:
        control_tabs = ["Login", "Dark Mode"]
    return await render_template('overview.html', backend="quart_project", frontend="jinja", database="postgresql", tabs=tabs, control_tabs=control_tabs)