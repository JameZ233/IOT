from machine import Pin
import utime

builtin_led = Pin(0, Pin.OUT)
antenna_led = Pin(2, Pin.OUT)
builtin_led.value(0)
antenna_led.value(0)
counter=0
while True:
    counter=counter+1
    if counter % 2 == 0:
        builtin_led.value(not builtin_led.value())
    if counter % 3 == 0:
        antenna_led.value(not antenna_led.value())
        print('1')
    utime.sleep(0.5)
    
