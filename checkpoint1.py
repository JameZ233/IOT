from machine import Pin, ADC, PWM
import utime, builtins
FREQUENCY = 256
#sampling frequency 1 hz
SAMP_FREQ = 0.1

led = Pin(12, Pin.OUT)
pwd_led = PWM(led)

piezzo = Pin(13, Pin.OUT)
pwd_piezzo = PWM(piezzo)

# light_sensor = Pin(9, Pin.IN)
adc = ADC(0)


pwd_led.freq(FREQUENCY)
# pwd_led.duty(DUTY_CYCLE)
pwd_piezzo.freq(FREQUENCY)
# pwd_piezzo.duty(DUTY_CYCLE)


while True:
    light_value = adc.read()
    # light_value = 512
    pwd_led.duty(light_value)
    pwd_piezzo.duty(light_value //4)
    builtins.print(light_value)
    utime.sleep(SAMP_FREQ)
    