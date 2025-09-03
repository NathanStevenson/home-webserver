import uvicorn
from quart import Quart, render_template
from quart_schema import QuartSchema, validate_request, validate_response
from quart_project.db_interface import db_interface
from quart_project import html_routes
from quart_auth import QuartAuth
from quart_project.secrets.secrets import app_secret_key
from quart_project import user_authentication

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

    # this config file is used by WebWeaver to ensure your web app does exactly what you specified
    if webweaver_config:
        app.config.update(webweaver_config)
    
    # Before serving the webserver: initialize the database connection; if the project has one
    @app.before_serving
    async def before_serving():
        await db_interface.init_db()

    return app