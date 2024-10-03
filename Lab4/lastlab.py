from lab3_hz2994_nw2568_tz2642_check2 import *
from lab3_hz2994_nw2568_tz2642_check3 import *
import lab3_hz2994_nw2568_tz2642_check3 as lab3_hz2994_nw2568_tz2642_check3

def main():
    # Start the system (integrate alarm check and time display)
    while True:
        oled.fill(0)
        adjust_brightness()
        if lab3_hz2994_nw2568_tz2642_check3.mode_idx == 5:
            display_alarm()
        else:
            display_time()
        oled.show()
        check_alarm()
        utime.sleep(0.1)