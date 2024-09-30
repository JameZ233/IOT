from machine import PWM
from checkpoint1 import *
import checkpoint1

FREQUENCY = 256

# Buzzer or vibration motor setup
buzzer = Pin(15, Pin.OUT)  # Assuming Pin 15 is used for the alarm buzzer/motor
pwm_buzzer=PWM(buzzer)
pwm_buzzer.freq(FREQUENCY)

# Timer for debounce
debounce_timer = Timer(-1)

# Debounce time in milliseconds
DEBOUNCE_TIME = 200

# Time modification modes
modes = ["year", "month", "day", "hour", "minute","alarm"]
mode_idx = 0  # Start with "year"
# add alarm mode to modes
modes.append("alarm")

# Variables to store alarm time
alarm_set = False
alarm_hour = None  # 15
alarm_minute = None  # 30

# Function to display time on OLED
def display_time():
    # while True:
    # oled.fill(0)  # Clear the screen
    current_time = rtc.datetime()  # Fetch current time
    builtins.print(current_time)
    formatted_date = "{:04}-{:02}-{:02}".format(current_time[0], current_time[1], current_time[2])  # YYYY-MM-DD
    formatted_time = "{:02}:{:02}:{:02}".format(current_time[4], current_time[5], current_time[6])  # HH:MM:SS
    oled.text(formatted_date, 0, 0)
    oled.text(formatted_time, 0, 20)
    oled.text("Mode: " + modes[mode_idx], 0, 40)
    # oled.show()
    #utime.sleep(1)

# Function to display alarm on OLED
def display_alarm():
    oled.text("Set Alarm:", 0, 0)
    formatted_hr = "--" if alarm_hour is None else "{:02}".format(alarm_hour)
    formatted_min = "--" if alarm_minute is None else "{:02}".format(alarm_minute)
    oled.text(formatted_hr + ":" + formatted_min, 0, 20)

# Set alarm at alarm mode & cycle through modes (override)
def switch_mode():
    global mode_idx, alarm_set
    if mode_idx == 5:
        if alarm_hour is not None and alarm_minute is not None:
            alarm_set = True
            builtins.print('set alarm')
        else:
            alarm_set = False
            builtins.print('disable alarm')
    mode_idx = (mode_idx + 1) % len(modes)

# override switch_mode
checkpoint1.switch_mode = switch_mode

# Increment or decrement the selected time unit (override)
def modify_time(change):
    builtins.print('Go through here')
    if mode_idx == 0:  # year
        set_year(change)
    elif mode_idx == 1:  # month
        set_month(change)
    elif mode_idx == 2:  # day
        set_day(change)
    elif mode_idx == 3:  # hour
        set_hour(change)
    elif mode_idx == 4:  # minute
        set_minute(change)
    elif mode_idx == 5:  # alarm
        set_alarm(change)

# override modify_time
checkpoint1.modify_time = modify_time

# Increment hour or minute of alarm
def set_alarm(change):
    global alarm_hour, alarm_minute
    if change > 0:
        if alarm_hour is None:
            alarm_hour = 0
        else:
            alarm_hour = (alarm_hour + 1) % 25
            if alarm_hour == 24:
                alarm_hour = None
    elif change < 0:
        if alarm_minute is None:
            alarm_minute = 0
        else:
            alarm_minute = (alarm_minute + 1) % 61
            if alarm_minute == 60:
                alarm_minute = None

# Function to check if alarm time has been reached
def check_alarm():
    current_time = rtc.datetime()
    builtins.print('cuurent time:', current_time)
    if alarm_set and current_time[4] == alarm_hour and current_time[5] == alarm_minute:
        trigger_alarm()

# Function to trigger the alarm
def trigger_alarm():
    oled.fill(0)
    oled.text("ALARM!", 0, 0)
    oled.show()
    pwm_buzzer.duty(512)
    utime.sleep(5)
    pwm_buzzer.duty(0)

# Attach interrupt to the buttons (falling and rising edge)
button_inc.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=button_isr)
button_dec.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=button_isr)
button_mode.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=button_isr)

# Start the system (integrate alarm check and time display)
# while True:
#     oled.fill(0)
#     if mode_idx == 5:
#         display_alarm()
#     else:
#         display_time()
#     oled.show()
#     builtins.print(mode_idx)
#     check_alarm()
#     utime.sleep(1)
