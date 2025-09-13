import quart
from quart import Quart
from quart_schema import QuartSchema
from quart_project.db_interface import db_interface
from quart_project import html_routes
from quart_auth import QuartAuth, Unauthorized
from quart_project.secrets.secrets import app_secret_key
from quart_project import user_authentication
from quart_project import video_streaming
from quart_project import updating_led

# returns a fully configured Quart application
def create_app(webweaver_config=None):
    app = Quart(__name__, template_folder="/home/nathan/home-webserver/jinja", static_folder="/home/nathan/home-webserver/jinja/static")
    # have to keep this constant - initial connection is HTTPS over Tailscale funnel then locally it is HTTP so still secure
    app.config["QUART_AUTH_COOKIE_SECURE"] = False
    QuartSchema(app)
    # Custom Quart Authentication; Standard Web Based and Bearer API Based
    # Quart-Auth Documentation: https://quart-auth.readthedocs.io/en/latest/tutorials/quickstart.html
    app.secret_key = app_secret_key
    QuartAuth(app)

    # registers all of your top level routes / (HMTL routes), /api (JSON API routes)
    app.register_blueprint(html_routes.bp)
    app.register_blueprint(user_authentication.bp)
    app.register_blueprint(video_streaming.bp)
    app.register_blueprint(updating_led.bp)

    # this config file is used by WebWeaver to ensure your web app does exactly what you specified
    if webweaver_config:
        app.config.update(webweaver_config)
    
    # Before serving the webserver: initialize the database connection; if the project has one
    @app.before_serving
    async def before_serving():
        await db_interface.init_db()
        # camera[id] -> { user[id] -> websocket queue }
        app.camera_websocket_conns = {}

    # if you fail a login requirement instead of default 401 unauthorized serve this custom 
    @app.errorhandler(Unauthorized)
    async def custom_unauthorized_page(error):
        tabs = ["Overview"]
        control_tabs = ["Login", "Dark Mode"]
        return await quart.render_template('unauthorized.html', tabs=tabs, control_tabs=control_tabs)

    return app