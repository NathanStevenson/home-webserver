# Home Server

FUTURE
- Add different colored logging and try and find a way to silence the DB logs - 10 min
- Change the wrap flag to a scroll flag (text should always wrap to display properly -- add the flag to scroll - would be cool if title stayed put and rest of text scrolled)
- link LED to User pairing instead of name do it like with Calendar Event where we foreign key it (so users can change their username) - 30 min
- turn LED off clear canvas choice
- Add recipes to the website (extra easy thing) - FRI CHILL / DO SUNDAY


## Perfecting Video Streaming
* Wireguard does not work, MediaMTX huge pain in the ass (10s+ slow unless WebRTC, AWS expensive asf)


picam2 = Picamera2()
video_config = picam2.create_video_configuration(main={"size": (1280, 720), "format": "RGB888"})
picam2.configure(video_config)

encoder = H264Encoder(repeat=True, iperiod=30, framerate=30)
output = FfmpegOutput("-f rtsp -rtsp_transport udp rtsp://localhost:8554/cam", audio=False)

picam2.start_encoder(encoder, output)
picam2.start()


- USB Microphone (small) - $10

LED Cost:
- Rpi Zero W 15, MicroSD 4, LED 29, LED Bonnet 18, Power 19, GPIO Pin hammer In 6: $91

Camera Cost:
- Rpi Zero 2 W (way faster) 24, MicroSD 4, Camera 15, Camera Ribbon Adapter 6, Power 12: $61

- Future project ALWAYS get Rpi Zero 2WH with the GPIO pins on the board $28 on amazon - find cheaper at actual hardware sites (digikey, vilros)
- Good speed and comes with everything needed out of the box

Total all 3: $243, $10 on book, $50 on dinner
~$300; prolly 30 hours of work 