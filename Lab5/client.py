import socket
import json
import time

def send_command(command):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("10.206.27.162", 8081))  # Replace with ESP IP address
    s.send(json.dumps(command).encode('utf-8'))
    s.close()

# Example commandspy
screen_on_command = {"name": "screen_on", "args": []}
screen_off_command={"name": "screen_off", "args": []}
display_time = {"name": "display_time", "args": []}
set_alarm_command = {"name": "set_alarm", "args": [15, 30]}
display_location = {"name": "display_location", "args":[]}
display_weather = {"name": "display_weather", "args":[]}

if __name__ == "__main__":
    send_command(screen_on_command)
    time.sleep(2)
    send_command(screen_off_command)
    time.sleep(2)
    send_command(display_time)
    time.sleep(5)
    send_command(set_alarm_command)
    time.sleep(5)
    send_command(display_location)
    time.sleep(3)
    send_command(display_weather)
    time.sleep(3)