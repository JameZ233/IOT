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
now = utime.localtime()
builtins.print('now1',now)
rtc.datetime((now[0],now[1],now[2],now[6],now[3],now[4],now[5],0))  # Example hardcoded datetime (YYYY, M, D, Weekday, H, M, S, Subsecond)
builtins.print('nowtime',rtc.datetime())

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
            builtins.print('Increment')
        elif pin == button_dec:
            modify_time(-1)
            builtins.print('Decrement')
        elif pin == button_mode:
            switch_mode()
            builtins.print('Switch mode')
        # button_pressed = True
    # else:
        # button_pressed = False
    # Re-enable interrupt after debounce
    pin.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=button_isr)

# Debounce function for buttons
# def debounce(pin):
#     if not pin.value():
#         utime.sleep_ms(200)  # delay for debouncing
#     return pin.value()

# Function to display time on OLED
def display_time():
    # while True:
    oled.fill(0)  # Clear the screen
    current_time = rtc.datetime()  # Fetch current time
    builtins.print(current_time)
    formatted_date = "{:04}-{:02}-{:02}".format(current_time[0], current_time[1], current_time[2])  # YYYY-MM-DD
    formatted_time = "{:02}:{:02}:{:02}".format(current_time[4], current_time[5], current_time[6])  # HH:MM:SS
    oled.text(formatted_date, 0, 0)
    oled.text(formatted_time, 0, 20)
    oled.text("Mode: " + modes[mode_idx], 0, 40)
    oled.show()
    #utime.sleep(1)

# Cycle through modes
def switch_mode():
    global mode_idx
    mode_idx = (mode_idx + 1) % len(modes)

# Checks if a given year is a leap year
def is_leap_year(yr):
    return (yr % 4 == 0) and (yr % 100 != 0 or yr % 400 == 0)

# Set year within 0~9999 range
def set_year(cur_time, change):
    new_year = cur_time[0] + change
    if new_year < 0:
        new_year = 9999
    elif new_year > 9999:
        new_year = 0
    cur_time[0] = new_year

# Set month within 1~12 range
def set_month(cur_time, change):
    new_month = cur_time[1] + change
    if new_month < 1:
        new_month = 12
    elif new_month > 12:
        new_month = 1
    cur_time[1] = new_month

# Set day within 1~28/29/30/31 range w.r.t. month
def set_day(cur_time, change):
    new_day = cur_time[2] + change
    match cur_time[1]:
        case 1, 3, 5, 7, 8, 10, 12:
            if new_day > 31:
                new_day = 1
            elif new_day < 1:
                new_day = 31
        case 4, 6, 9, 11:
            if new_day > 30:
                new_day = 1
            elif new_day < 1:
                new_day = 30
        case 2:
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

# Set hour within 0~23 range
def set_hour(cur_time, change):
    new_hour = cur_time[4] + change
    if new_hour < 0:
        new_hour = 23
    elif new_hour > 23:
        new_hour = 0
    cur_time[4] = new_hour

# Set minite within 0~59 range
def set_minute(cur_time, change):
    new_minute = cur_time[5] + change
    if new_minute < 0:
        new_minute = 59
    elif new_minute > 59:
        new_minute = 0
    cur_time[5] = new_minute

# Increment or decrement the selected time unit
def modify_time(change):
    cur_time = list(rtc.datetime())
    match mode_idx:
        case 0:  # year
            set_year(cur_time, change)
        case 1:  # month
            set_month(cur_time, change)
        case 2:  # day
            set_day(cur_time, change)
        case 3:  # hour
            set_hour(cur_time, change)
        case 4:  # minute
            set_minute(cur_time, change)
    rtc.datetime(tuple(cur_time))

# Attach interrupt to the buttons (falling and rising edge)
button_inc.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=button_isr)
button_dec.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=button_isr)
button_mode.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=button_isr)

# Main loop
while True:
    display_time()
    utime.sleep(1)

# Function to increment time
# def inc_time():
#     current_time = list(rtc.datetime())
#     current_time[4] = (current_time[4] + 1) % 24  # Increment hour and wrap around after 23
#     rtc.datetime(tuple(current_time))

# Function to decrement time
# def dec_time():
#     current_time = list(rtc.datetime())
#     current_time[4] = (current_time[4] - 1) % 24  # Decrement hour and wrap around after 0
#     rtc.datetime(tuple(current_time))

# Function to select mode
# def select_mode():
    # rtc.datetime((2024, 9, 25, 2, 15, 30, 0, 0))  # Reset to the original time

# Start displaying time
# display_time()
