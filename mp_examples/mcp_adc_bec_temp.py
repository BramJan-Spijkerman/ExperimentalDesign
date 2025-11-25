from machine import SPI
from machine import Pin, ADC, UART, freq
from time import sleep, localtime

spi2 = SPI(1, 400000, polarity=1, phase=1, bits=8, firstbit=SPI.MSB, sck=Pin(10), mosi=Pin(11), miso=Pin(12))

led = Pin(25, Pin.OUT)
CS2 = Pin(13, Pin.OUT)

write=bytearray([0x06, 0x00, 0x00])
read=bytearray(3)
n=0
while(True):
    for c in range(8):
        # A D C    M C P 3 2 0 8
        write=bytearray([0x06+((c>>2)&1), ((c&3)<<6), 0x00])
        CS2.low()
        spi2.write_readinto(write,read)
        CS2.high()
        print("{:04d} ".format(int(1.38*((read[1] & 0x1F) << 8 | read[2]))),end="")
    print()
    led.toggle()
    sleep(1)
