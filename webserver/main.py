from reader import read_temperature
from utime import sleep
from wifi import connect
from request import send_data
from setup import device_name

connect()  

while True: 
    temperature = read_temperature()
    print(f"Temperature: {temperature} C")
    send_data(temperature)
    print("sent")
    sleep(5)  # Wait for 1 second before reading again
