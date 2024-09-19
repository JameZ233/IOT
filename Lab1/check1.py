from machine import Pin
import utime

builtin_led = Pin(0, Pin.OUT)
builtin_led.value(1)

while True:
    for i in range (6):
        builtin_led.value(not builtin_led.value())
        utime.sleep(0.5)
    
    for i in range (6):
        builtin_led.value(not builtin_led.value())
        utime.sleep(1)

    for i in range (6):
        builtin_led.value(not builtin_led.value())
        utime.sleep(0.5)
    utime.sleep(2)