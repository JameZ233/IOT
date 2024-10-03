from machine import Pin, SPI
from utime import sleep
from builtins import print
from lab3_hz2994_nw2568_tz2642_check2 import *
from lab3_hz2994_nw2568_tz2642_check3 import *
import lab3_hz2994_nw2568_tz2642_check3 as lab3_hz2994_nw2568_tz2642_check3

#Initialize Hardware SPI
spi = SPI(1, baudrate=1500000, polarity=1, phase=1)
cs = Pin(16, Pin.OUT)

#SPI Read/Write Bit
SPI_READ =1 << 7
SPI_WRITE =0 << 7

#Whether or not to read multiple bytes
SPI_SINGLE_BYTE = 0 << 6
SPI_MULTIPLE_BYTES = 1 << 6

#Read ID register
read_buffer = bytearray(7)
# ID_REG = 0x00

# ADXL345 register addresses
ADXL345_REG_DEVID = 0x00
ADXL345_REG_POWER_CTL = 0x2D
ADXL345_REG_DATAX0 = 0x32
# AXES_REG = 0x32
# X2_REG = 0x33
# Y1_REG = 0x34
# Y2_REG = 0x35
# Z1_REG = 0x36
# Z2_REG = 0x37

# Read from a register
def read_register(reg, length=1):
    cs.value(0)
    # spi.write(bytearray([reg | SPI_READ]))   # Set the MSB to 1 for reading
    # data = spi.read(length)
    spi.readinto(read_buffer, SPI_READ | SPI_MULTIPLE_BYTES | reg)
    cs.value(1)
    # return data

# Write to a register
def write_register(reg, value):
    cs.value(0)
    spi.write(bytearray([reg | SPI_WRITE, value]))  # Set the MSB to 0 for writing
    cs.value(1)

# Initialize ADXL345 (put it into measurement mode)
def adxl345_init():
    # device_id = read_register(ADXL345_REG_DEVID)[0]
    # print("Device ID:", hex(device_id))
    # Put the device into measurement mode (set measure bit to 1)
    write_register(ADXL345_REG_POWER_CTL, 0x08)


# Read accelerometer data
def read_acceleration():
    read_register(ADXL345_REG_DATAX0)
    x=two_conplement(read_buffer[1:3])
    y=two_conplement(read_buffer[3:5])
    z=two_conplement(read_buffer[5:7])
    # data = read_register(ADXL345_REG_DATAX0, 6)  # Read 6 bytes starting at DATAX0
    # x = data[0:2]
    # y = data[2:4]
    # z = data[4:6]
    # x = int.from_bytes(data[0:2], 'little', signed=True)
    # y = int.from_bytes(data[2:4], 'little', signed=True)
    # z = int.from_bytes(data[4:6], 'little', signed=True)
    return x, y, z

def two_conplement(a):
    a = a[1] << 8 | a[0]
    if a >32767:
        a -= 65536
    return a

def scroll(x,y):
    global x_res, y_res
    if abs(x) > abs(y):
        # y_res=0
        if x>0:
            x_res -=1 
        else: 
            x_res += 1
    else: 
        # x_res=0
        if y>0:
            y_res +=1
        else:
            y_res -=1

# Initialize the ADXL345
adxl345_init()
x_res=0
y_res=0
# Main loop to read acceleration data
while True:
    x, y, z = read_acceleration()
    print('X: {}, Y: {}, Z: {}'.format(x, y, z))
    scroll(x,y)
    oled.fill(0)
    adjust_brightness(x_res,y_res)
    if lab3_hz2994_nw2568_tz2642_check3.mode_idx == 5:
        display_alarm()
    else:
        display_time(x_res,y_res)
    oled.show()
    check_alarm()
    sleep(0.5)