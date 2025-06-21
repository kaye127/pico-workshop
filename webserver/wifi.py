import network
from utime import sleep

def connect():
    try:
        wlan = network.WLAN(network.STA_IF)
        if not wlan.active():
            wlan.active(True)

        if wlan.isconnected():
            print("Already connected to WiFi:", wlan.ifconfig())
            return True

        print("Connecting to WiFi...")
        wlan.connect('LOGICXP', 'l0g1cxp24!x')

        timeout = 10
        for _ in range(timeout):
            if wlan.isconnected():
                print("✅ Connected to WiFi:", wlan.ifconfig())
                return True
            sleep(1)

        print("Connection timed out")
        return False

    except Exception as e:
        print(f"Error during WiFi connection: {e}")
        return False
