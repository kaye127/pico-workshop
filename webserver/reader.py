from setup import temp

def read_temperature():
    adc_value = temp.read_u16()
    voltage = adc_value * (3.3 / 65535)  # Converting ADC value to voltage
    temperature_celsius = 27 - (voltage - 0.706) / 0.001721  # Converting voltage to Celsius
    return round(temperature_celsius,1)