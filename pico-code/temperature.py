import network
import time
import machine
import ujson
import uwebsockets.client as websockets

# ==== USER CONFIGURATION ====
SSID = 'LOGICXP'
PASSWORD = 'l0g1cxp24!'
USERNAME = 'jane'
DEVICE_NAME = f"{USERNAME}-pico"
WS_URL = f"wss://back-9n0o.onrender.com/ws/{DEVICE_NAME}"

# ==== HARDWARE SETUP ====
led = machine.Pin(28, machine.Pin.OUT)
sensor = machine.ADC(4)  # Internal temperature sensor

# ==== CONNECT TO WI-FI ====
def connect_to_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print(f"Connecting to Wi-Fi: {SSID}")
        wlan.connect(SSID, PASSWORD)
        while not wlan.isconnected():
            time.sleep(0.5)
            print("Waiting for connection...")
    print("✅ Connected to Wi-Fi:", wlan.ifconfig())

# ==== READ TEMPERATURE ====
def read_temperature():
    raw = sensor.read_u16()
    voltage = (raw / 65535.0) * 3.3
    temperature = 27 - (voltage - 0.706) / 0.001721
    return round(temperature, 2)

# ==== MAIN LOOP ====
def websocket_loop():
    while True:
        try:
            print(f"🔌 Connecting to WebSocket at {WS_URL}")
            ws = websockets.connect(WS_URL)
            print("✅ WebSocket connected")

            last_send = time.time()

            while True:
                # Send temperature every 10 seconds
                now = time.time()
                if now - last_send >= 10:
                    temp = read_temperature()
                    ws.send(ujson.dumps({"temp": temp}))
                    print("📤 Sent temperature:", temp)
                    last_send = now

                # Check for commands
                try:
                    ws.settimeout(0.2)
                    msg = ws.recv()
                    if msg:
                        print("📥 Received:", msg)

                        # Try JSON first
                        try:
                            data = ujson.loads(msg)
                            cmd = data.get("command", "")
                        except:
                            cmd = msg  # fallback to raw string

                        if cmd == "led_on":
                            led.value(1)
                            print("💡 LED turned ON")
                        elif cmd == "led_off":
                            led.value(0)
                            print("💡 LED turned OFF")

                except Exception:
                    pass  # Timeout, no message

                time.sleep(0.1)  # Yield to CPU

        except Exception as e:
            print("⚠️ WebSocket error:", e)
            print("🔄 Reconnecting in 5 seconds...")
            time.sleep(5)

# ==== START ====
connect_to_wifi()
websocket_loop()
