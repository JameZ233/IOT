import network
import urequests
import ujson
import ssd1306
from machine import Pin, I2C
from builtins import print

# Connect to Wi-Fi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect('Columbia University', '')  # Replace with your Wi-Fi credentials
    while not wlan.isconnected():
        pass
    print('Connected to Wi-Fi')

# Display on OLED
i2c = I2C(scl=Pin(5), sda=Pin(4))
oled = ssd1306.SSD1306_I2C(128, 32, i2c)

def display_coords(latitude, longitude):
    oled.fill(0)
    oled.text("Lat: " + str(latitude), 0, 0)
    oled.text("Lon: " + str(longitude), 0, 16)
    oled.show()

# Fetch Geolocation
def get_geolocation():
    url = "http://ip-api.com/json"
    response = urequests.get(url)
    data = ujson.loads(response.text)
    return data['lat'], data['lon']

# Main
connect_wifi()
latitude, longitude = get_geolocation()
display_coords(latitude, longitude)
print('Showing coords')