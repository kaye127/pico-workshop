from reader import read_temperature
from utime import sleep
from wifi import connect

# connect()  

while True: 
    temperature = read_temperature()
    print(f"Temperature: {temperature} C")
    sleep(1)  # Wait for 1 second before reading again