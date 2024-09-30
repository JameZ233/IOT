from checkpoint2 import *
from checkpoint3 import *
import checkpoint3

def main():
    # Start the system (integrate alarm check and time display)
    while True:
        oled.fill(0)
        adjust_brightness()
        if checkpoint3.mode_idx == 5:
            display_alarm()
        else:
            display_time()
        oled.show()
        check_alarm()
        utime.sleep(0.1)