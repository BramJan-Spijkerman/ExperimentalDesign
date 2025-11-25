from machine import UART, Pin
import time

startTime = time.time()
#serial1 = serial.Serial('COM5',baudrate=9600,parity=serial.PARITY_EVEN,bytesize=8)  # open serial port
uart = UART(0,9600, parity=0, stop=1, bits=8, rx=Pin(1), tx=Pin(0))

inti = 0
while time.time() < startTime + 60:
    inti= inti - 1
    uart.write(('hello\n'+str(inti)).encode('utf-8'))
    print(uart.readline())
    time.sleep(1)
print('Serial port closed')

