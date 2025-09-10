import quart
import requests
import asyncio
import functools
from quart import redirect, url_for, request, websocket, current_app
from quart_schema import validate_request
from quart_auth import login_required, login_user, logout_user, AuthUser, current_user

from ..db_interface.camera_model import Camera
from ..db_interface.user_model import User
from ..db_interface import db_interface
from . import schemas
from . import auth_utils

bp = quart.Blueprint('video_streaming', __name__, url_prefix="/stream")

# Small helper to run requests in a thread so Quart's loop stays unblocked
def _requests_get(url: str, timeout: float = 3.0):
    return requests.get(url, timeout=timeout)

async def http_get(url: str, timeout: float = 3.0):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, functools.partial(_requests_get, url, timeout))

# Optional: simple auth check for ingest (e.g., token query)
def verify_ingest(request_args) -> bool:
    # Example: token=shared-secret (replace with something real)
    token = request_args.get("token")
    return token == "replace-with-a-strong-secret"

# ---------- WebSocket: Pi -> Central (ingest) ----------

@bp.websocket("/ws/ingest/<int:camera_id>")
async def ws_ingest(camera_id: int):
    # Want to ensure only verified pi camera devices are streaming here
    if not verify_ingest(request.args):
        await websocket.close(1008)  # policy violation
        return

    async with db_interface.create_session() as session:
        camera = await Camera.get_by_id(session, camera_id)
        if camera is None:
            await websocket.close(1003)
            return

    # Pull binary data from the websocket and place it in the queue of all clients subscribed to it
    async def receiving():
        try:
            while True:
                video_data = await websocket.receive()
                # get the dict of user[id] -> websocket send queue for each camera
                users_attached = current_app.camera_websocket_conns[camera_id]
                for socket_queue in users_attached.values():
                    socket_queue.put_nowait(video_data)

        except Exception as e:
            print("Exception thrown when ingesting camera feed from pi: ", camera_id, e)

    # Every 30s send a ping to the picamera when streaming to keep socket alive
    async def sending():
        try:
            while True:
                await asyncio.sleep(30)
                try:
                    await websocket.ping()
                except Exception:
                    break
        finally:
            pass

    producer = asyncio.create_task(sending())
    consumer = asyncio.create_task(receiving())
    await asyncio.gather(producer, consumer)

# ---------- WebSocket: Central -> Clients (view) ----------

@bp.websocket("/ws/view/<int:camera_id>")
@login_required
async def ws_view(camera_id: int):
    try:
        # Each connected client gets its own queue - if user/camera does not exist then close websocket cannot stream
        queue = asyncio.Queue()
        user_id = current_user.auth_id
        async with db_interface.create_session() as session:
            camera = await Camera.get_by_id(session, camera_id)
            if camera is None or user_id is None:
                await websocket.close(1003)
                return
            else:
                print(f"Connection Request to Camera {camera_id} by User {user_id}")
                # add the queue and the user to the specific cameras IDs dictionary
                users_attached = current_app.camera_websocket_conns[camera_id]
                users_attached[user_id] = queue
                # if first user must submit req to pi to start streaming - otherwise streaming has started and by adding the queue to dict you will subscribe to it
                if len(users_attached) == 1:
                    await begin_video_streaming(camera_id)

        # Pull binary data being shoved into asyncio queue and send it out to the end user client
        async def sending():
            try:
                while True:
                    frame = await queue.get()
                    await websocket.send(frame)
            except asyncio.CancelledError:
                print(f"Unsubscribing user {user_id} from Camera {camera_id} in sending()")
                await unsubscribe_user_to_camera(user_id, camera_id)
            except Exception:
                pass

        async def receiving():
            try:
                while True:
                    data = await websocket.receive()
            except asyncio.CancelledError:
                print(f"Unsubscribing user {user_id} from Camera {camera_id} in receiving()")
                await unsubscribe_user_to_camera(user_id, camera_id)

        producer = asyncio.create_task(sending())
        consumer = asyncio.create_task(receiving())
        await asyncio.gather(producer, consumer)

    # if the websocket connection drops then need unsubscribe user from websocket - may need to stop streaming pi -> server too
    except asyncio.CancelledError:
        print(f"Unsubscribing user {user_id} from Camera {camera_id} in top level websocket")
        await unsubscribe_user_to_camera(user_id, camera_id)

# Alert client pi to start streaming video to server
async def begin_video_streaming(camera_id):
    try:
        print(f"Requesting to begin video streams for camera {camera_id}")
        async with db_interface.create_session() as session:
            camera = await Camera.get_by_id(session, camera_id)
            await http_get(f"http://{camera.ip_address}:{camera.port}/on")

    except Exception as e:
        print("Exception when starting video stream", e)

# Unsubscribe a given user from the camera streaming socket queue; if the camera now has no one connected alert client pi to stop streaming video to server to save network traffic
async def unsubscribe_user_to_camera(user_id, camera_id):
    try:
        # get the current users attached to the camera
        users_attached = current_app.camera_websocket_conns[camera_id]
        del users_attached[user_id]
        print(f"Unsubscribed user {user_id} from camera {camera_id}. Currently {len(users_attached)} users remaining")

        # if as a result no users are attached then alert client pi to stop streaming
        if len(users_attached) == 0:
            print(f"Requesting to stop video streams for camera {camera_id}")
            async with db_interface.create_session() as session:
                camera = await Camera.get_by_id(session, camera_id)
                await http_get(f"http://{camera.ip_address}:{camera.port}/off")

    except Exception as e:
        print("Exception when starting video stream", e)