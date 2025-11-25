from machine import Pin, Timer
from random import randint
import utime
 
dir_pin = Pin(16, Pin.OUT)
step_pin = Pin(17, Pin.OUT)
steps_per_revolution = 200
 
# Initialize timer
tim = Timer()
 
def step(t):
    global step_pin
    step_pin.value(not step_pin.value())
 
def rotate_motor(delay):
    # Set up timer for stepping
    tim.init(freq=1000000//delay, mode=Timer.PERIODIC, callback=step)
 
def loop():
    while True:
        # Set motor direction clockwise
        dir_pin.value(0)

        #dir_pin.value(randint(0,1))
 
        # Spin motor randomly
        #rotate_motor(500*randint(1,2))
        #utime.sleep_ms(int(steps_per_revolution*0.25*randint(1,4)))
        #tim.deinit()  # stop the timer
        #utime.sleep(randint(1,4)*0.03125)

        rotate_motor(500)
        utime.sleep_ms(steps_per_revolution)
        tim.deinit()  # stop the timer
        utime.sleep(2)


if __name__ == '__main__':
    loop()