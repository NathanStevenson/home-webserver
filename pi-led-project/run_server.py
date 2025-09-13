import uvicorn
import requests
import json

from quart import Quart, jsonify
from quart_schema import validate_request

import led_utils
import schemas

app = Quart(__name__)

# ======== CONFIG (unique per Pi) ========
PI_NAME     = "nathan"                                          # change per device
CENTRAL_WS  = "http://192.168.8.21:8000/led/pi_info/" + PI_NAME # server URL to ping on boot
# =======================================

# Right now LED board does not exist so the led_utils.display_text(msg, color=(0,0,255), wrap=True) - is commented out above all the print statements for now
# This is just to ensure the general logic is working - once the LED parts come in connect everything together and flip the commented lines and test displaying to LED
@app.post("/update_led_screen")
@validate_request(schemas.UpdateLedScreen)
async def update_led_screen(data: schemas.UpdateLedScreen):
    # led_utils.display_text(data.message, color=data.color, wrap=data.wrapText)
    print(f"Displaying message to LED: {data.message} {data.color} {data.wrapText}")
    return jsonify( {"status": "updated_screen"} )

if __name__ == "__main__":
    # on boot reach out to the central server to get the updated info for the pi
    response = requests.get(CENTRAL_WS)
    # if successful then display
    if response.status_code == 200:
        data = response.json()
        # led_utils.display_text(data.pi_message, color=data.pi_color, wrap=data.pi_wrap)
        print(f'Displaying message to LED: {data["pi_message"]} {data["pi_color"]} {data["pi_wrap"]}')

    # Run the tiny control server that central will call
    uvicorn.run("run_server:app", host="0.0.0.0", port=8000, timeout_graceful_shutdown=3)
