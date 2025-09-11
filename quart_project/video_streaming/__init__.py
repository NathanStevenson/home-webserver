import quart
import requests
import asyncio
import functools
from quart import request, websocket, current_app
from quart_auth import login_required, current_user

from ..db_interface.camera_model import Camera
from ..db_interface.user_model import User
from ..db_interface import db_interface

bp = quart.Blueprint('video_streaming', __name__, url_prefix="/stream")

# HTML route which serves the HTML + JS + CSS used to connect to pi streaming client
@bp.get("video")
@login_required
async def stream_video():
    async with db_interface.create_session() as session:
        logged_in_user_info = await User.get_by_id(session, int(current_user.auth_id))

    return await quart.render_template('stream_video.html', logged_in_user_info=logged_in_user_info)



# Small helper to run requests in a thread so Quart's loop stays unblocked
def _requests_get(url: str, timeout: float = 3.0):
    return requests.get(url, timeout=timeout)

async def http_get(url: str, timeout: float = 3.0):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, functools.partial(_requests_get, url, timeout))

# ---------- WebSocket: Pi -> Central (ingest) ----------

# white listed pi-camera IPs
white_listed_ips = ["192.168.8.22"]

@bp.websocket("/ws/ingest/<int:camera_id>")
async def ws_ingest(camera_id: int):
    # Want to ensure only verified pi camera devices are streaming here
    client = websocket.remote_addr
    if client not in white_listed_ips:
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
                # add the queue and the user to the specific cameras IDs dictionary - if not camera ID then return an empty dict
                current_app.camera_websocket_conns[camera_id] = {}
                current_app.camera_websocket_conns[camera_id][user_id] = queue
                # if first user must submit req to pi to start streaming - otherwise streaming has started and by adding the queue to dict you will subscribe to it
                if len(current_app.camera_websocket_conns[camera_id]) == 1:
                    await begin_video_streaming(camera_id)

        # Pull binary data being shoved into asyncio queue and send it out to the end user client
        async def sending():
            while True:
                frame = await queue.get()
                await websocket.send(frame)

        async def receiving():
            while True:
                data = await websocket.receive()
            

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
        del current_app.camera_websocket_conns[camera_id][user_id]
        print(f"Unsubscribed user {user_id} from camera {camera_id}. Currently {len(current_app.camera_websocket_conns[camera_id])} users remaining")

        # if as a result no users are attached then alert client pi to stop streaming
        if len(current_app.camera_websocket_conns[camera_id]) == 0:
            print(f"Requesting to stop video streams for camera {camera_id}")
            async with db_interface.create_session() as session:
                camera = await Camera.get_by_id(session, camera_id)
                await http_get(f"http://{camera.ip_address}:{camera.port}/off")

    except Exception as e:
        print("Exception when stopping video stream", e)