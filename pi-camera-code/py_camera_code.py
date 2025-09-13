import asyncio
import uvicorn
from typing import Optional

from quart import Quart, request, jsonify
import websockets
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
import cv2

app = Quart(__name__)

# ======== CONFIG (unique per Pi) ========
CAMERA_ID = 1               # change per device
CENTRAL_WS = "ws://192.168.8.21:8000/stream/ws/ingest"  # central server base
FRAMERATE = 40
# =======================================

stream_task: Optional[asyncio.Task] = None

async def camera_streamer(camera_id: str):
    """Continuously capture JPEGs with Picamera2 and send over WebSocket."""
    uri = f"{CENTRAL_WS}/{camera_id}"

    picam2 = Picamera2()
    config = picam2.create_video_configuration(
        main={"size": (640, 480), "format": "RGB888"} # trying to mess with the res by making it lower to see if less choppy next play with framerate; if neither work then need to stream over TCP/UDP then websocket not websocket to websocket 
    )
    picam2.configure(config)
    encoder = H264Encoder(1000000)
    picam2.encoders = encoder
    picam2.start()

    try:
        while True:
            try:
                async with websockets.connect(uri, max_size=None) as ws:
                    while True:
                        # Capture JPEG frame
                        frame = picam2.capture_array("main")
                        # Encode as JPEG in-memory and send the buffer byutes through the socket
                        ret, buffer = cv2.imencode(".jpg", frame)
                        await ws.send(buffer.tobytes())

                        await asyncio.sleep(1 / FRAMERATE)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"[WARN] Connection failed: {e}, retrying in 2s...")
                await asyncio.sleep(2)
    finally:
        picam2.stop()
        picam2.close()

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
    uvicorn.run("app", host="0.0.0.0", port=8000, reload=True, timeout_graceful_shutdown=3)