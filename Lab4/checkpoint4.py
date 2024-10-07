import urequests
import time
import network
import urequests
import ujson
import ssd1306

# Push Notification URL (replace with your unique channel)
ntfy_url = 'http://ntfy.sh/'

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

# Data to send (coordinates and weather)
message = {
    'topic':'zwz',
    'title': 'Weather Update',
    'message': 'Lat: {} Long: {} Temp: {} C'.format(latitude, longitude, temperature)
}

# data=ujson.dumps(message)

# Send push notification
response = urequests.post(ntfy_url, json=message)

print(response.status_code)
print(response.text)

# Check response
if response.status_code == 200:
    print('Notification sent successfully')
else:
    print('Failed to send notification')

# Optional: Wait to avoid spamming the API
time.sleep(10)