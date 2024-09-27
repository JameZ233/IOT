from machine import PWM
# Pin, I2C, RTC, 
# from ssd1306 import SSD1306_I2C
# import utime, builtins
from checkpoint1 import *

FREQUENCY = 256

# Initialize I2C for OLED (modify pins based on your board setup)
# i2c = I2C(scl=Pin(5), sda=Pin(4))
# oled_width = 128
# oled_height = 32
# oled = SSD1306_I2C(oled_width, oled_height, i2c)

# Initialize the RTC (real-time clock)
# rtc = RTC()
# now=utime.localtime()
# builtins.print('now1',now)
# rtc.datetime((now[0],now[1],now[2],now[6],now[3],now[4],now[5],0))  # Example hardcoded datetime (YYYY, M, D, Weekday, H, M, S, Subsecond)
# builtins.print('nowtime',rtc.datetime())

# Button pins (modify based on your button setup)
# button1 = Pin(12, Pin.IN, Pin.PULL_UP)  # To increase time
# button2 = Pin(13, Pin.IN, Pin.PULL_UP)  # To decrease time
# button3 = Pin(14, Pin.IN, Pin.PULL_UP)  # To reset time

# Buzzer or vibration motor setup
buzzer = Pin(15, Pin.OUT)  # Assuming Pin 15 is used for the alarm buzzer/motor
pwm_buzzer=PWM(buzzer)
pwm_buzzer.freq(FREQUENCY)

# Debounce function for buttons (reusable from Lab 2)
# def debounce(pin):
#     utime.sleep_ms(200)  # delay for debouncing
#     return pin.value()

# Function to display time on OLED
# def display_time():

#     oled.fill(0)  # Clear the screen
#     current_time = rtc.datetime()  # Fetch current time
#     builtins.print(current_time)
#     formatted_time = "{:02}:{:02}:{:02}".format(current_time[4], current_time[5], current_time[6])  # HH:MM:SS
#     oled.text("Time:", 0, 0)
#     oled.text(formatted_time, 0, 20)
#     oled.show()

#     # Check buttons and modify time accordingly
#     if debounce(button1) == 0:
#         increment_hour()
#         builtins.print('Increment')
#     elif debounce(button2) == 0:
#         decrement_hour()
#         builtins.print('Decrement')
#     elif debounce(button3) == 0:
#         reset_time()
#         builtins.print('reset')

# Function to increment hours
# def increment_hour():
#     current_time = list(rtc.datetime())
#     current_time[4] = (current_time[4] + 1) % 24  # Increment hour and wrap around after 23
#     rtc.datetime(tuple(current_time))

# Function to decrement hours
# def decrement_hour():
#     current_time = list(rtc.datetime())
#     current_time[4] = (current_time[4] - 1) % 24  # Decrement hour and wrap around after 0
#     rtc.datetime(tuple(current_time))

# Function to reset time (hardcoded)
# def reset_time():
#     rtc.datetime((2024, 9, 25, 2, 15, 30, 0, 0))  # Reset to the original time

# Variables to store alarm time
alarm_set = False
alarm_hour = 15
alarm_minute = 30

# Function to set the alarm
def set_alarm():
    global alarm_set, alarm_hour, alarm_minute
    while True:
        if debounce(button1) == 0:
            alarm_hour = (alarm_hour + 1) % 24
        elif debounce(button2) == 0:
            alarm_minute = (alarm_minute + 1) % 60
        elif debounce(button3) == 0:
            alarm_set = True
            break  # Exit after setting alarm

        oled.fill(0)
        oled.text("Set Alarm:", 0, 0)
        formatted_alarm = "{:02}:{:02}".format(alarm_hour, alarm_minute)
        oled.text(formatted_alarm, 0, 20)
        oled.show()
        utime.sleep(0.2)

# Function to check if alarm time has been reached
def check_alarm():
    global alarm_set
    current_time = rtc.datetime()
    builtins.print('cuurent time',current_time)
    if alarm_set and current_time[4] == alarm_hour and current_time[5] == alarm_minute:
        trigger_alarm()

# Function to trigger the alarm
def trigger_alarm():
    oled.fill(0)
    oled.text("ALARM!", 0, 0)
    oled.show()
    pwm_buzzer.on()
    utime.sleep(5)
    pwm_buzzer.off()
    # utime.sleep(0.5)

# Run alarm setup first
set_alarm()

# Start the system (integrate alarm check and time display)
while True:
    
    check_alarm()
    display_time()
    utime.sleep(1)
