from machine import Pin, PWM, ADC, Timer
import time, builtins

# Setup pins
button_pin = Pin(15, Pin.IN, Pin.PULL_UP)  # GPIO15 as input with pull-up

# Timer for debounce
debounce_timer = Timer(-1)

# Debounce time in milliseconds
DEBOUNCE_TIME = 200

# System state
button_pressed = False

# Interrupt Service Routine for the button
def button_isr(pin):
    global button_pressed
    # Disable the interrupt temporarily
    button_pin.irq(handler=None)
    
    # Start debounce timer
    debounce_timer.init(mode=Timer.ONE_SHOT, period=DEBOUNCE_TIME, callback=debounce_callback)

def debounce_callback(timer):
    global button_pressed

    # Re-enable interrupt after debounce
    if button_pin.value():  # Button pressed (value is 0)
        button_pressed = True
    else:
        button_pressed = False
    
    button_pin.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=button_isr)
# Attach interrupt to the button (falling and rising edge)
button_pin.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=button_isr)

# Main loop
while True:
    builtins.print(button_pressed)
    time.sleep(0.1)