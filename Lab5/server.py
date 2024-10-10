import socket
import json
from machine import Pin, I2C, RTC, Timer, PWM
from ssd1306 import SSD1306_I2C
import utime, builtins
import urequests
import time
import network
import urequests
import ujson

# Initialize I2C for OLED
FREQUENCY = 256
i2c = I2C(scl=Pin(5), sda=Pin(4))
oled_width = 128
oled_height = 32
oled = SSD1306_I2C(oled_width, oled_height, i2c)
buzzer = Pin(15, Pin.OUT)  # Assuming Pin 15 is used for the alarm buzzer/motor
pwm_buzzer=PWM(buzzer)
pwm_buzzer.freq(FREQUENCY)

# Initialize the RTC (real-time clock)
rtc = RTC()
rtc.datetime((2024, 9, 30, 0, 15, 30, 0, 0))
now = utime.localtime()
builtins.print('utime.localtime():', now)
rtc.datetime((now[0],now[1],now[2],now[6],now[3],now[4],now[5],0))  # Example hardcoded datetime (YYYY, M, D, Weekday, H, M, S, Subsecond)
builtins.print('rtc.datetime():', rtc.datetime())

# Time modification modes
modes = ["year", "month", "day", "hour", "minute"]
mode_idx = 0  # Start with "year"

# Define functions for smartwatch operations
def screen_on():
    oled.fill(0)
    oled.text('Adafruit',0,0)
    oled.show()

def screen_off():
    oled.fill(0)
    oled.show()

def display_time():
    oled.fill(0)
    builtins.print('Displaying time')
    current_time = rtc.datetime()  # Fetch current time
    builtins.print('check1idx',mode_idx)
    formatted_date = "{:04}-{:02}-{:02}".format(current_time[0], current_time[1], current_time[2])  # YYYY-MM-DD
    formatted_time = "{:02}:{:02}:{:02}".format(current_time[4], current_time[5], current_time[6])  # HH:MM:SS
    oled.text(formatted_date, 0, 0)
    oled.text(formatted_time, 0, 12)
    oled.show()

def set_alarm(alarm_hour, alarm_minute):
    current_time = rtc.datetime()
    builtins.print('cuurent time:', current_time)
    if current_time[4] == alarm_hour and current_time[5] == alarm_minute:
        trigger_alarm()
    
# Function to trigger the alarm
def trigger_alarm():
    oled.fill(0)
    oled.text("ALARM!", 0, 0)
    oled.show()
    pwm_buzzer.duty(512)
    utime.sleep(5)
    pwm_buzzer.duty(0)

# Connect to Wi-Fi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect('Columbia University', '')  # Replace with your Wi-Fi credentials
    while not wlan.isconnected():
        pass
    print('Connected to Wi-Fi')

def get_geolocation():
    url = "http://ip-api.com/json"
    response = urequests.get(url)
    data = ujson.loads(response.text)
    return data['lat'], data['lon']

def display_location():
    latitude,longitude = get_geolocation()
    oled.fill(0)
    oled.text("Lat: " + str(latitude), 0, 0)
    oled.text("Lon: " + str(longitude), 0, 16)
    oled.show()

def display_weather():
    latitude,longitude = get_geolocation()
    api_key = '3126b12a48cfeefb8433649e17e59361'
    weather_url = 'http://api.openweathermap.org/data/2.5/weather?lat={}&lon={}&appid={}&units=metric'.format(latitude, longitude, api_key)
    response = urequests.get(weather_url)
    weather_data = response.json()
    temperature = weather_data['main']['temp']
    description = weather_data['weather'][0]['description']
    oled.fill(0)
    oled.text('Temp: {} C'.format(temperature), 0, 0)
    oled.text('Desc: {}'.format(description), 0, 16)
    oled.show()

# Map commands to smartwatch functions
command_map = {
    "screen_on": screen_on,
    "screen_off": screen_off,
    "display_time": display_time,
    "set_alarm": set_alarm,
    'display_location': display_location,
    'display_weather': display_weather
}

# Server code for ESP8266 to receive and process commands
def run_server():
    addr = socket.getaddrinfo('0.0.0.0', 8081)[0][-1]
    s = socket.socket()
    s.bind(addr)
    s.listen(1)
    print('Run through')
    while True:
        cl, addr = s.accept()
        print("Client connected from", addr)
        try:
            data = cl.recv(1024)
            if data:
                command = json.loads(data.decode('utf-8'))
                function_name = command.get("name")
                args = command.get("args", [])
                
                # Execute the corresponding function
                if function_name in command_map:
                    command_map[function_name](*args)
                else:
                    print("Unknown command")
        finally:
            cl.close()

run_server()