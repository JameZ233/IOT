from checkpoint2 import *
from checkpoint3 import *

while True:
    oled.fill(0)
    adjust_brightness()
    if mode_idx == 5:
        display_alarm()
    else:
        display_time()
    oled.show()
    check_alarm()
    utime.sleep(1)