# Description

This repo contains the complete codebase for all parts of the automated SmartHome. The central webserver, LED Raspberry Pis, PiCamera, and any other technologies added in the future

## Central Webserver

This can be downloaded on a new machine by creating a new virtual environment `python3 -m venv venv` and then downloading all of the dependencies via `./venv/bin/pip install requirements.txt`


## PiCamera

This can be downloaded on a new machine by creating a new virtual environment `python3 -m venv venv` and then downloading all of the dependencies via `./venv/bin/pip install requirements.txt`. This will download the websockets and the lightweight webserver; however the code for the PiCamera is better to be installed via apt for the best experience. 

After installing the PiCamera dependencies via `sudo apt install -y python3-picamera2` and `sudo apt install -y libcap-dev` then run `python3 -m venv venv --system-site-packages`. This flag will allow the virtual environment to include packages found in the system's `site-packages` (where apt will install the Picamera code) if the dependency is not currently found within the virtual environment.

Also need to run `./venv/bin/pip install --upgrade numpy opencv-python` for cv2 dependency to be comptaible with the new numpy2 dependency released in 2024


## LED Project

`sudo rmmod snd_bcm2835` this is needed to get the pi zero working on boot

1. Need to download and install build tools

``` bash
sudo apt-get update
sudo apt-get install -y \
    git \
    python3-dev \
    python3-pillow \
    python3-venv \
    build-essential \
    cmake \
    libopenjp2-7 \
    libtiff5
```

2. Clone and Build RGB LED Python matrix

```
cd ~
git clone https://github.com/hzeller/rpi-rgb-led-matrix.git
cd rpi-rgb-led-matrix
make build-python PYTHON=$(which python3)
```

3. Install everything in a Python VENV

```
cd ~/rpi-rgb-led-matrix
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip

make install-python PYTHON=$(which python3)
```

4. Copy over the `/pi-led-project` directory to the desired machine. This folder contains all the source code needed to host a lightweight webserver for updating the board as well as a service file which can be copied into `/etc/systemd/system` and will allow it to function as a Linux systemd service which will be called upon boot everytime.

5. Certifi certs DO NOT work on RPi-Zero 32 bit need to install and use our own certificates in order to perform requests to a HTTPS website. If below does not work can set verify=False but this is not reccommended

```
sudo apt install ca-certificates
sudo update-ca-certificates

export SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt
```