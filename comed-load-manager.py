#!/usr/bin/env python3
"""
comed-load-manager.py

Subscribes to ComEd 5-minute pricing via MQTT and controls a TP-Link
smart plug (via python-kasa) to reduce load when prices are high.

State is held in memory. On startup, the current outlet state is queried
and used as the initial state. The first price reading then determines
whether to change it.

Control logic:
  - Turn OFF when price > OFF_THRESHOLD
  - Turn ON  when price has been consistently <= ON_THRESHOLD
                for at least ON_DELAY_MINUTES

Designed to be extended with additional MQTT subscriptions (e.g. humidity).
"""

import json
import time
import logging
import paho.mqtt.client as mqtt

# =============================================================================
# Configuration — adjust these before running
# =============================================================================

MQTT_BROKER      = "mqtt"
MQTT_PORT        = 1883
PRICE_TOPIC      = "HA/trixi/comed/5_minute_cost"

PLUG_HOST        = "tpplug11"

OFF_THRESHOLD    = 8.0    # cents/kWh — turn off load above this
ON_THRESHOLD     = 8.0    # cents/kWh — candidate threshold for turning back on
ON_DELAY_MINUTES = 30     # minutes price must stay <= ON_THRESHOLD before turning on

LOG_LEVEL        = logging.DEBUG

# =============================================================================
# Logging
# =============================================================================

logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s %(levelname)-8s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

# =============================================================================
# State
# =============================================================================

class State:
    def __init__(self):
        self.plug_on          = None   # True/False/None (None = unknown until queried)
        self.last_price       = None   # most recent price reading
        self.last_price_time  = None   # wall-clock time of last reading (time.time())
        self.below_since      = None   # time.time() when price first dropped <= ON_THRESHOLD
                                       # None if price is currently above threshold

state = State()

# =============================================================================
# Plug control stubs — replace print() calls with kasa calls when ready
# =============================================================================

def query_plug_state() -> bool:
    """Return current plug state. Stub: assumes ON until kasa is wired up."""
    log.info("STUB query_plug_state() → assuming ON")
    return True

def turn_plug_off():
    log.info("DECISION: turning plug OFF (price above threshold)")
    # TODO: asyncio.run(plug.turn_off()) via kasa

def turn_plug_on():
    log.info("DECISION: turning plug ON (price below threshold for required period)")
    # TODO: asyncio.run(plug.turn_on()) via kasa

# =============================================================================
# Price logic
# =============================================================================

def handle_price(price: float, price_t: int, t: int):
    """Called for each new price reading. Implements hysteresis control."""

    now = time.time()
    age = int(now - price_t)
    log.debug(f"Price reading: {price}¢/kWh  price_t={price_t}  age={age}s")

    state.last_price      = price
    state.last_price_time = now

    if price > OFF_THRESHOLD:
        # Price is high — turn off if currently on
        state.below_since = None   # reset the recovery timer
        if state.plug_on:
            turn_plug_off()
            state.plug_on = False
        else:
            log.debug("Price high but plug already off — no action")

    else:
        # Price is at or below ON_THRESHOLD
        if state.plug_on:
            log.debug("Price acceptable and plug already on — no action")
            state.below_since = None  # no need to track; we're already on
        else:
            # Plug is off — start or continue the recovery timer
            if state.below_since is None:
                state.below_since = now
                log.info(f"Price dropped to {price}¢ — starting {ON_DELAY_MINUTES}m recovery timer")
            else:
                elapsed = (now - state.below_since) / 60.0
                remaining = ON_DELAY_MINUTES - elapsed
                if remaining <= 0:
                    turn_plug_on()
                    state.plug_on = True
                    state.below_since = None
                else:
                    log.info(f"Price {price}¢ below threshold for {elapsed:.1f}m "
                             f"— {remaining:.1f}m remaining before turn-on")

# =============================================================================
# MQTT callbacks
# =============================================================================

def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        log.info(f"Connected to MQTT broker {MQTT_BROKER}:{MQTT_PORT}")
        client.subscribe(PRICE_TOPIC)
        log.info(f"Subscribed to {PRICE_TOPIC}")
    else:
        log.error(f"MQTT connect failed: reason_code={reason_code}")

def on_message(client, userdata, msg):
    topic = msg.topic
    try:
        payload = json.loads(msg.payload.decode())
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        log.warning(f"Unparseable message on {topic}: {e}  raw={msg.payload}")
        return

    if topic == PRICE_TOPIC:
        try:
            price   = float(payload["price"])
            price_t = int(payload["price_t"])
            t       = int(payload["t"])
        except (KeyError, ValueError) as e:
            log.warning(f"Unexpected payload structure: {e}  payload={payload}")
            return
        handle_price(price, price_t, t)

    # Additional topic handlers go here as elif branches

def on_disconnect(client, userdata, flags, reason_code, properties):
    if reason_code != 0:
        log.warning(f"Unexpected disconnect: reason_code={reason_code} — paho will retry")

# =============================================================================
# Main
# =============================================================================

def main():
    log.info("comed-load-manager starting")

    # Query initial plug state before subscribing to prices
    state.plug_on = query_plug_state()
    log.info(f"Initial plug state: {'ON' if state.plug_on else 'OFF'}")

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect    = on_connect
    client.on_message    = on_message
    client.on_disconnect = on_disconnect

    client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
    client.loop_forever()

if __name__ == "__main__":
    main()
