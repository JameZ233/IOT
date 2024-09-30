from machine import Pin, I2C, RTC, Timer
from ssd1306 import SSD1306_I2C
import utime, builtins

# Initialize I2C for OLED
i2c = I2C(scl=Pin(5), sda=Pin(4))
oled_width = 128
oled_height = 32
oled = SSD1306_I2C(oled_width, oled_height, i2c)

# Initialize the RTC (real-time clock)
rtc = RTC()
rtc.datetime((2024, 9, 30, 0, 15, 30, 0, 0))
now = utime.localtime()
builtins.print('utime.localtime():', now)
rtc.datetime((now[0],now[1],now[2],now[6],now[3],now[4],now[5],0))  # Example hardcoded datetime (YYYY, M, D, Weekday, H, M, S, Subsecond)
builtins.print('rtc.datetime():', rtc.datetime())

# Button pins
button_inc = Pin(12, Pin.IN, Pin.PULL_UP)  # To increase time
button_dec = Pin(13, Pin.IN, Pin.PULL_UP)  # To decrease time
button_mode = Pin(14, Pin.IN, Pin.PULL_UP)  # To select mode

# Timer for debounce
debounce_timer = Timer(-1)

# Debounce time in milliseconds
DEBOUNCE_TIME = 200

# Time modification modes
modes = ["year", "month", "day", "hour", "minute"]
mode_idx = 0  # Start with "year"

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
    pin.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=button_isr)

# Function to display time on OLED
def display_time():
    current_time = rtc.datetime()  # Fetch current time
    builtins.print('check1idx',mode_idx)
    formatted_date = "{:04}-{:02}-{:02}".format(current_time[0], current_time[1], current_time[2])  # YYYY-MM-DD
    formatted_time = "{:02}:{:02}:{:02}".format(current_time[4], current_time[5], current_time[6])  # HH:MM:SS
    oled.text(formatted_date, 0, 0)
    oled.text(formatted_time, 0, 12)
    oled.text("Mode: " + modes[mode_idx], 0, 24)

# Cycle through modes
def switch_mode():
    global mode_idx
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

# Increment or decrement the selected time unit
def modify_time(change):
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
    # rtc.datetime(tuple(cur_time))

# Attach interrupt to the buttons (falling and rising edge)
button_inc.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=button_isr)
button_dec.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=button_isr)
button_mode.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=button_isr)

def main():
# Main loop
    while True:
        oled.fill(0)
        display_time()
        oled.show()
        utime.sleep(1)