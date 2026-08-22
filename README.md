# comed-load-manager

Manage load based on Comed 5 minute price reports. This is intended to be used to control a dehumidifier so there will be some logic related to that. This is intended for Comed customers who have signed up for Comed hourly pricing.

* <https://hourlypricing.comed.com/live-prices/>

## AI/LLM warning

This is developed with the assistance of Claude Sonnet 4.6 using the Web portal (at <https://claude.ai/chat/f0607ebe-49e1-4b4c-828c-5296adb7132b for me but probably won't work for you.>)

## Status

* 2026-08-21 working script with no actual control implemented. It just printe what decisions would be made.

## Outline

Subscribe to locally generated MQTT messages that report 5 minute Comed demand prices and turn the smart socket that controls the dehumidifier on or off depending on the price. If the price exceeds a threshold, turn the smart socket off and keep off until the prioce has dropped below a set threshold for a predetermined time.

## Requirements

* "MQTT client class (Python 3)" 2.1.0 provided on Debian Trixie by `python3-paho-mqtt`
* "python-kasa" found at <https://github.com/python-kasa/python-kasa> and installed in a python virtual environment (venv).
* `python3.14-venv` or similar, depending on your Python3 version.

## Deploying

### CLI


```text
sudo apt install python3-paho-mqtt python3.14-venv # Or as appropriate for your OS/distro
cd ~/Projects # or some convenient location.
git clone git@github.com:HankB/comed-load-manager.git # or git clone https://github.com/HankB/comed-load-mamager.git
cd comed-load-mamager # Why didn't this work?
python3 -m venv --system-site-packages .venv
source .venv/bin/activate
pip install git+https://github.com/python-kasa/python-kasa.git
python3 -c "from kasa import Discover; print('kasa ok')" # confirm library availability
```

```text
export KASA_USERNAME="your TP-Link username"
export KASA_PASSWORD="your TP-Link password"
./comed-load-manager.py
```
