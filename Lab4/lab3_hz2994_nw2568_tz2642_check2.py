from machine import ADC
from lab3_hz2994_nw2568_tz2642_check1 import *

# Light sensor (assuming photoresistor on ADC pin A0)
light_sensor = ADC(0)  # Pin A0

# Function to map sensor value to brightness level
def map_brightness(value):
    # Assume light_sensor value ranges from 0 (dark) to 1023 (bright)
    # Scale it to a value suitable for screen brightness (0 - 255)
    return int(value / 1023 * 255)

# Function to adjust brightness based on ambient light
def adjust_brightness(x,y):
    sensor_value = light_sensor.read()  # Read the light sensor
    builtins.print('lightvalue: ', sensor_value)
    brightness = map_brightness(sensor_value)  # Map to brightness
    oled.contrast(brightness)  # Adjust the OLED contrast
    # oled.text('Brightness', 80, 0)
    oled.text(str(sensor_value), (90+x)%128, (20+y)%32)

def main():
# Start brightness adjustment and time display
    while True:
        oled.fill(0)
        display_time()
        adjust_brightness()
        oled.show()
        utime.sleep(0.1)
