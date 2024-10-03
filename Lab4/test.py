from machine import Pin, SPI
import time
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
read_buffer = bytearray(2)
ID_REG = 0x00

cs.value(0)
spi.readinto(read_buffer, SPI_READ | SPI_SINGLE_BYTE | ID_REG)
cs.value(1)

print(read_buffer)