# Description

This repo contains the complete codebase for all parts of the automated SmartHome. The central webserver, LED Raspberry Pis, PiCamera, and any other technologies added in the future

## Central Webserver

This can be downloaded on a new machine by creating a new virtual environment `python3 -m venv venv` and then downloading all of the dependencies via `./venv/bin/pip install requirements.txt`


## PiCamera

This can be downloaded on a new machine by creating a new virtual environment `python3 -m venv venv` and then downloading all of the dependencies via `./venv/bin/pip install requirements.txt`. This will download the websockets and the lightweight webserver; however the code for the PiCamera is better to be installed via apt for the best experience. 

After installing the PiCamera dependencies via `sudo apt install -y python3-picamera2` and `sudo apt install -y libcap-dev` then run `python3 -m venv venv --system-site-packages`. This flag will allow the virtual environment to include packages found in the system's `site-packages` (where apt will install the Picamera code) if the dependency is not currently found within the virtual environment.

Also need to run `./venv/bin/pip install --upgrade numpy opencv-python` for cv2 dependency to be comptaible with the new numpy2 dependency released in 2024