from machine import PWM, Pin, I2C, RTC, Timer 
from ssd1306 import SSD1306_I2C
import utime, builtins

FREQUENCY = 256

# Initialize I2C for OLED (modify pins based on your board setup)
i2c = I2C(scl=Pin(5), sda=Pin(4))
oled_width = 128
oled_height = 32
oled = SSD1306_I2C(oled_width, oled_height, i2c)

# Initialize the RTC (real-time clock)
rtc = RTC()
now=utime.localtime()
builtins.print('now1',now)
rtc.datetime((now[0],now[1],now[2],now[6],now[3],now[4],now[5],0))  # Example hardcoded datetime (YYYY, M, D, Weekday, H, M, S, Subsecond)
builtins.print('nowtime',rtc.datetime())

# Button pins (modify based on your button setup)
button_inc = Pin(12, Pin.IN, Pin.PULL_UP)  # To increase time
button_dec = Pin(13, Pin.IN, Pin.PULL_UP)  # To decrease time
button_mode = Pin(14, Pin.IN, Pin.PULL_UP)  # To reset time

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
# modes.append("alarm")

# Interrupt Service Routine for the button
def button_isr(pin):
    # global button_pressed
    # Disable the interrupt temporarily
    pin.irq(handler=None)
    
    # Start debounce timer
    debounce_timer.init(mode=Timer.ONE_SHOT, period=DEBOUNCE_TIME, callback=lambda t:debounce_callback(t, pin))

def debounce_callback(timer, pin):
    # global button_pressed
    if not pin.value():  # Button pressed (value is 0)
        if pin == button_inc:
            modify_time(1)
            builtins.print('inc btn pressed')
        elif pin == button_dec:
            modify_time(-1)
            builtins.print('dec btn pressed')
        elif pin == button_mode:
            switch_mode()
            builtins.print('switch mode')
        # button_pressed = True
    # else:
        # button_pressed = False
    # Re-enable interrupt after debounce
    pin.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=button_isr)

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
alarm_hour = 14  # 15
alarm_minute = 29  # 30

# Interrupt Service Routine for the button
# def button_isr(pin):
#     global mode_idx
#     # Disable the interrupt temporarily
#     pin.irq(handler=None)
    
#     # Start debounce timer
#     if mode_idx == 5:
#         debounce_timer.init(mode=Timer.ONE_SHOT, period=DEBOUNCE_TIME, callback=lambda t:alarm_callback(t, pin))
#     else:
#         debounce_timer.init(mode=Timer.ONE_SHOT, period=DEBOUNCE_TIME, callback=lambda t:debounce_callback(t, pin))

# Interrupt Service Routine for the alarm
# def alarm_isr(pin):
#     # Disable the interrupt temporarily
#     pin.irq(handler=None)
    
#     # Start debounce timer
#     debounce_timer.init(mode=Timer.ONE_SHOT, period=DEBOUNCE_TIME, callback=lambda t:alarm_callback(t, pin))

# def alarm_callback(timer, pin):
#     global alarm_set
#     if not pin.value():  # Button pressed (value is 0)
#         if pin == button_inc:
#             modify_alarm('hour')
#             builtins.print('Increment alarm hour')
#         elif pin == button_dec:
#             modify_alarm('minute')
#             builtins.print('Increment alarm minute')
#         elif pin == button_mode:
#             alarm_set = True
#             switch_mode()
#             builtins.print('Set alarm & switch mode')
#         # button_pressed = True
#     # else:
#         # button_pressed = False
#     # Re-enable interrupt after debounce
#     # if mode_idx == 5:
#     #     pin.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=alarm_isr)
#     # else:
#         # Attach interrupt to the alarm button (falling and rising edge)
#     pin.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=button_isr)

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


# Checks if a given year is a leap year
def is_leap_year(yr):
    return (yr % 4 == 0) and (yr % 100 != 0 or yr % 400 == 0)

# Set year within 0~9999 range
def set_year(change):
    cur_time = list(rtc.datetime())
    new_year = cur_time[0] + change
    if new_year < 0:
        new_year = 9999
    elif new_year > 9999:
        new_year = 0
    cur_time[0] = new_year
    rtc.datetime(tuple(cur_time))

# Set month within 1~12 range
def set_month(change):
    cur_time = list(rtc.datetime())
    new_month = cur_time[1] + change
    if new_month < 1:
        new_month = 12
    elif new_month > 12:
        new_month = 1
    cur_time[1] = new_month
    rtc.datetime(tuple(cur_time))

# Set day within 1~28/29/30/31 range w.r.t. month
def set_day(change):
    cur_time = list(rtc.datetime())
    new_day = cur_time[2] + change
    
    # January, March, May, July, August, October, December (months with 31 days)
    if cur_time[1] in [1, 3, 5, 7, 8, 10, 12]:
        if new_day > 31:
            new_day = 1
        elif new_day < 1:
            new_day = 31
    
    # April, June, September, November (months with 30 days)
    elif cur_time[1] in [4, 6, 9, 11]:
        if new_day > 30:
            new_day = 1
        elif new_day < 1:
            new_day = 30
    
    # February
    elif cur_time[1] == 2:
        if is_leap_year(cur_time[0]):
            if new_day > 29:
                new_day = 1
            elif new_day < 1:
                new_day = 29
        else:
            if new_day > 28:
                new_day = 1
            elif new_day < 1:
                new_day = 28
    
    cur_time[2] = new_day
    rtc.datetime(tuple(cur_time))


# Set hour within 0~23 range
def set_hour(change):
    cur_time = list(rtc.datetime())
    new_hour = cur_time[4] + change
    if new_hour < 0:
        new_hour = 23
    elif new_hour > 23:
        new_hour = 0
    cur_time[4] = new_hour
    rtc.datetime(tuple(cur_time))

# Set minite within 0~59 range
def set_minute(change):
    cur_time = list(rtc.datetime())
    new_minute = cur_time[5] + change
    if new_minute < 0:
        new_minute = 59
    elif new_minute > 59:
        new_minute = 0
    cur_time[5] = new_minute
    rtc.datetime(tuple(cur_time))

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
