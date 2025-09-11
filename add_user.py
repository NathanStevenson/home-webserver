
# This file can be run locally to add a new username / password to the auth DB (no routes are exposed to sign up as we want only explicit users to be able to access the site)
import asyncio
import sys

from quart_project.db_interface import db_interface
from quart_project.db_interface.user_model import User
from quart_project.db_interface.camera_model import Camera
from quart_project.user_authentication import auth_utils

# Will add a new username, email, and password each time this script is run into the DB
async def process_add_user(email, username, password):
    await db_interface.init_db()

    async with db_interface.create_session() as session:
        user_exists = await User.get_user_by_email(session, email)
        if user_exists is not None:
            return {"error_msg": f"Email already exists for {email}. Try logging in or signing up with another email"}
        else:
            # salt + hash the incoming password via bcrypt; create a new user; add it to SQLAlchemy session; put it in DB
            hashed_password = auth_utils.hash_password(password)
            new_user = User(email=email, hashed_password=hashed_password, username=username)
            await User.add(session, new_user)

# Will add a new camera into the DB
async def process_add_camera(location, ip_address):
    async with db_interface.create_session() as session:
        await db_interface.init_db()
        new_camera = Camera(location=location, ip_address=ip_address)
        await Camera.add(session, new_camera)

# add username with CLP (email, username, password)
# EXAMPLE:
# ./venv/bin/python3 add_user.py <email> <username> <pwd> --> this command will add the new user with this email to the db
# ./venv/bin/python3 add_user.py <location> <ip> --> this command will add the new camera to the db
if __name__ == "__main__":
    asyncio.run(process_add_user(sys.argv[1], sys.argv[2], sys.argv[3]))
    # asyncio.run(process_add_camera(sys.argv[1], sys.argv[2]))
