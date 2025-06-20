import network

def connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Connecting to WiFi...")
        wlan.connect('ALS', 'L0g1c@2023!')
        while not wlan.isconnected():
            pass
    print('Connected to WiFi:', wlan.ifconfig()[0])

connect()