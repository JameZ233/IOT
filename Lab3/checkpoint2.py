from machine import ADC
# , Pin, I2C, RTC
# from ssd1306 import SSD1306_I2C
# import utime, builtins
from checkpoint1 import *

# Initialize I2C for OLED
# i2c = I2C(scl=Pin(5), sda=Pin(4))
# oled_width = 128
# oled_height = 32
# oled = SSD1306_I2C(oled_width, oled_height, i2c)

# Initialize RTC
# rtc = RTC()
# rtc.datetime((2024, 9, 25, 2, 15, 30, 0, 0))  # Hardcoded initial datetime

# Light sensor (assuming photoresistor on ADC pin A0)
light_sensor = ADC(0)  # Pin A0

# Function to map sensor value to brightness level
def map_brightness(value):
    # Assume light_sensor value ranges from 0 (dark) to 1023 (bright)
    # Scale it to a value suitable for screen brightness (0 - 255)
    return int(value / 1024 * 255)

# Function to adjust brightness based on ambient light
def adjust_brightness():
    # while True:
    sensor_value = light_sensor.read()  # Read the light sensor
    builtins.print('lightvalue: ', sensor_value)
    brightness = map_brightness(sensor_value)  # Map to brightness
        # current_time = rtc.datetime()
        # formatted_time = "{:02}:{:02}:{:02}".format(current_time[4], current_time[5], current_time[6])
    oled.contrast(brightness)  # Adjust the OLED contrast
        # oled.fill(0)
    # oled.text('Brightness', 64, 0)
    oled.text(str(sensor_value), 90, 20)
        # oled.text("Time:", 0, 0)
        # oled.text(formatted_time, 64, 0)
    oled.show()
        # utime.sleep(0.5)  # Small delay to prevent overloading

# Function to display the time on OLED
# def display_time():
#     while True:
#         oled.fill(0)
#         current_time = rtc.datetime()
#         formatted_time = "{:02}:{:02}:{:02}".format(current_time[4], current_time[5], current_time[6])
#         oled.text("Time:", 0, 0)
#         oled.text(formatted_time, 0, 20)
#         oled.show()
#         utime.sleep(1)

# Start brightness adjustment and time display
while True:
    display_time()
    adjust_brightness()
    utime.sleep(1)
