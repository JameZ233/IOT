from checkpoint2 import *
from checkpoint3 import *

if __name__ == "__main__":
    # Start the system (integrate alarm check and time display)
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