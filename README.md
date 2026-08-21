# comed-load-manager

Manage load based on Comed 5 minute price reports. This is intended to be used to control a dehumidifier so there will be some logic related to that. This is intended for Comed customers who have signed up for Comed hourly pricing.

* <https://hourlypricing.comed.com/live-prices/>

## 2026-08-21 AI/LLM warning


## 2026-08-21 Outline

Subscribe to locally generated MQTT messages that report 5 minute Comed demand prices and turn the smart socket that controls the dehumidifier on or off depending on the price. If the price exceeds a threshold, turn the smart socket off and keep off until the prioce has dropped below a set threshold for a predetermined time.

## .026-08-21 Requirements

* "MQTT client class (Python 3)" 2.1.0 provided on Debian Trixie by `python3-paho-mqtt`
* "python-kasa" found at <https://github.com/python-kasa/python-kasa> and installed in a python virtual environment (venv).
