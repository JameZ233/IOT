from machine import Pin, PWM, ADC, Timer
import time, builtins
FREQUENCY = 256
#sampling frequency 1 hz
SAMP_FREQ = 0.1

# Setup pins
button_pin = Pin(15, Pin.IN, Pin.PULL_UP)  # GPIO15 as input with pull-up
# button_pin.value(1)
led_pin = PWM(Pin(12, Pin.OUT), freq=FREQUENCY)  # GPIO13 as PWM for LED
light_sensor = ADC(0)  # ADC for light sensor
piezzo = Pin(13, Pin.OUT)
pwd_piezzo = PWM(piezzo, freq=FREQUENCY)

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
    # builtins.print('True2')
    # Re-enable interrupt after debounce
    if button_pin.value():  # Button pressed (value is 0)
        button_pressed = True
        # while True:
        #     builtins.print('True1')
        #     light_value = light_sensor.read()  # ADC value (0-1023)
        #     led_pin.duty(light_value)  # Set the brightness of LED (PWM duty cycle)
    else:
        button_pressed = False
        # led_pin.duty(0)
    
    button_pin.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=button_isr)
# Attach interrupt to the button (falling and rising edge)
button_pin.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=button_isr)

# Main loop
while True:
    if button_pressed:
        # Read from the light sensor
        light_value = light_sensor.read()  # ADC value (0-1023)
        led_pin.duty(light_value)  # Set the brightness of LED (PWM duty cycle)
        pwd_piezzo.duty(light_value //10)
        builtins.print(light_value //10)
    else:
        led_pin.duty(0)  # Turn off the LED when the button is released
        pwd_piezzo.duty(0)
    # builtins.print(button_pressed)
    time.sleep(SAMP_FREQ)