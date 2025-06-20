from machine import Pin
from utime import sleep

pin = Pin(28, Pin.OUT)

print("LED starts flashing...")
while True:
    try:
        pin.value(1)  # turn on the LED
        sleep(0.5)      # sleep 1sec
        pin.value(0)  # turn off the LED
        sleep(0.5)      # sleep 1sec
    except KeyboardInterrupt:
        break
pin.off()
print("Finished.")