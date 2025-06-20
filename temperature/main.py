import time

from machine import Pin, ADC

sensor = ADC(4)

def read_temperature():
    adc_value = sensor.read_u16()
    voltage = adc_value * (3.3 / 65535)  # Converting ADC value to voltage
    temperature_celsius = 27 - (voltage - 0.706) / 0.001721  # Converting voltage to Celsius
    return round(temperature_celsius,1)

while True:
    temperature = read_temperature()
    print("temperature: ", temperature)
    time.sleep(1)

