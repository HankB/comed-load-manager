# comed-load-manager

Manage load based on Comed 5 minute price reports. This is intended to be used to control a dehumidifier so there will be some logic related to that. This is intended for Comed customers who have signed up for Comed hourly pricing.

* <https://hourlypricing.comed.com/live-prices/>

## AI/LLM warning

This is developed with the assistance of Claude Sonnet 4.6 using the Web portal (at <https://claude.ai/chat/f0607ebe-49e1-4b4c-828c-5296adb7132b for me but probably won't work for you.>)

## Status

* 2026-08-24 Working playbook, second try and still manually editing comments which Claude overlooked twice.
* 2026-08-24 The first cut is deployed and working as desired.
* 2026-08-24 Added Systemd service file, credentials template and Ansible playbook. At present the playbok fails at `[Enable and start service]` but the Systemd operations can be completed manually.
* 2026-08-24 testing for several days is successful on a Pi 5 (until it crashed) and Pi CM4, both running Debian Forky. It is expected to work with Debian Trixie (stable) but these hosts just happened to be running Forky.
* 2026-08-23 tweak script to work with older Kasa plugs which do not require credentials.
* 2026-08-23 testing actual on/off control on Pi 5 running Debian Forky.
* 2026-08-21 working script with no actual control implemented. It just prints what decisions would be made.

## Outline

Subscribe to locally generated MQTT messages that report 5 minute Comed demand prices and turn the smart socket that controls the dehumidifier on or off depending on the price. If the price exceeds a threshold, turn the smart socket off and keep off until the price has dropped below a set threshold for a predetermined time.

## Requirements

* "MQTT client class (Python 3)" 2.1.0 provided on Debian Trixie by `python3-paho-mqtt`
* "python-kasa" found at <https://github.com/python-kasa/python-kasa> and installed in a python virtual environment (venv).
* `python3.14-venv` or similar, depending on your Python3 version.

## Plans

* This is intended to be used for a dehumidifier. There are possible other control strategies such as targeting a specific humidity level or perhaps on/off duty cycle. It is also conceivable that other loads could be controlled using this. If I were to implement something like that, I might consider a plug-in architecture that woula allow other control algorithms to be implemented as plug-ins. It might also be useful to implement plug-ins for the control outputs. At present I will continue to use this 'as is' and watch for opportunities for improvement. The dehumidifier I use can target a specific humidity and I am using that.

## Deploying

### CLI

To install:

```text
sudo apt install python3-paho-mqtt python3.14-venv # Or as appropriate for your OS/distro
cd ~/Projects # or some convenient location.
git clone git@github.com:HankB/comed-load-manager.git # or git clone https://github.com/HankB/comed-load-manager.git
cd comed-load-manager # Why didn't this work?
python3 -m venv --system-site-packages .venv
source .venv/bin/activate
pip install git+https://github.com/python-kasa/python-kasa.git
python3 -c "from kasa import Discover; print('kasa ok')" # confirm library availability
```

Once installed:

```text
cd ~/Projects/comed-load-manager # or some convenient location.
source .venv/bin/activate
export KASA_USERNAME="your TP-Link username"
export KASA_PASSWORD="your TP-Link password"
./comed-load-manager.py
```
