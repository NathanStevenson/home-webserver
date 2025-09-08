import quart
from quart import redirect, url_for
from quart_schema import validate_request
from quart_auth import login_required, login_user, logout_user, AuthUser, current_user

from ..db_interface.user_model import User
from ..db_interface import db_interface
from . import schemas
from . import auth_utils

bp = quart.Blueprint('authentication', __name__, url_prefix="/")