from machine import Pin,ADC

led = Pin(28, Pin.OUT)
temp = ADC(4)

server_url = "http://localhost:3000"

username = "jame"
device_name =  f"{username}-pico"




 