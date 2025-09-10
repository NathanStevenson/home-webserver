import asyncio
import io
import signal
from typing import Optional

from quart import Quart, request, jsonify
import websockets
import picamera

app = Quart(__name__)

# This will all be read in from a custom python file which will not be committed to the repo
# ======== CONFIG (unique per Pi) ========
CAMERA_ID = 1
CENTRAL_WS = "ws://192.168.8.21:8080/ws/ingest"  # central server base
INGEST_TOKEN = "replace-with-a-strong-secret"
FRAMERATE = 24
RESOLUTION = (1920, 1080)               # 1080p
# =======================================

stream_task: Optional[asyncio.Task] = None

async def camera_streamer(camera_id: id):
    uri = f"{CENTRAL_WS}/{camera_id}?token={INGEST_TOKEN}"
    # Reconnect loop (in case central restarts)
    while True:
        try:
            async with websockets.connect(uri, max_size=None) as ws:
                with picamera.PiCamera(resolution=RESOLUTION, framerate=FRAMERATE) as camera:
                    stream = io.BytesIO()
                    for _ in camera.capture_continuous(stream, format="jpeg", use_video_port=True):
                        await ws.send(stream.getvalue())
                        stream.seek(0)
                        stream.truncate()
        except asyncio.CancelledError:
            # graceful shutdown
            break
        except Exception:
            # brief backoff before retry
            await asyncio.sleep(1.0)

@app.route("/on")
async def turn_on():
    global stream_task
    requested_id = request.args.get("camera_id", default=CAMERA_ID)
    if stream_task and not stream_task.done():
        return jsonify({"status": "already_on", "camera_id": requested_id})
    loop = asyncio.get_running_loop()
    stream_task = loop.create_task(camera_streamer(requested_id))
    return jsonify({"status": "starting", "camera_id": requested_id})

@app.route("/off")
async def turn_off():
    global stream_task
    if stream_task and not stream_task.done():
        stream_task.cancel()
        try:
            await stream_task
        except asyncio.CancelledError:
            pass
        stream_task = None
        return jsonify({"status": "stopped"})
    return jsonify({"status": "already_off"})

if __name__ == "__main__":
    # Run the tiny control server that central will call
    app.run(host="0.0.0.0", port=8080, debug=False)
