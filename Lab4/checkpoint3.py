import network
import urequests
import ujson
import ssd1306
from machine import I2C, Pin

# OLED Setup
i2c = I2C(scl=Pin(5), sda=Pin(4))
oled = ssd1306.SSD1306_I2C(128, 32, i2c)

# Connect to Wi-Fi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect('Columbia University', '')  # Replace with your Wi-Fi credentials
    while not wlan.isconnected():
        pass
    print('Connected to Wi-Fi')

# Fetch Geolocation
def get_geolocation():
    url = "http://ip-api.com/json"
    response = urequests.get(url)
    data = ujson.loads(response.text)
    return data['lat'], data['lon']

# OpenWeatherMap API details
connect_wifi()
latitude, longitude = get_geolocation()
print(latitude)
print(longitude)
api_key = '3126b12a48cfeefb8433649e17e59361'
# latitude = 'your_latitude'
# longitude = 'your_longitude'
weather_url = 'http://api.openweathermap.org/data/2.5/weather?lat={}&lon={}&appid={}&units=metric'.format(latitude, longitude, api_key)

# Get weather data
response = urequests.get(weather_url)
weather_data = response.json()
print(weather_data)
# Extract relevant information
temperature = weather_data['main']['temp']
description = weather_data['weather'][0]['description']

# Display weather info on OLED
oled.fill(0)
oled.text('Temp: {} C'.format(temperature), 0, 0)
oled.text('Desc: {}'.format(description), 0, 16)
oled.show()