from machine import Pin, Timer
from random import randint
import utime

limit0_pin = Pin  (7, Pin.IN, Pin.PULL_DOWN)
limit1_pin = Pin(8, Pin.IN, Pin.PULL_DOWN)
m0_pin = Pin(9, Pin.OUT)
m1_pin = Pin(10, Pin.OUT)
m2_pin = Pin(11, Pin.OUT)
reset_pin = Pin(12, Pin.OUT)
sleep_pin = Pin(13, Pin.OUT)
step_pin = Pin(14, Pin.OUT)
dir_pin = Pin(15, Pin.OUT)
steps_per_revolution = 200
 
# Initialize timer
tim = Timer()
sleep_pin.value(0)
reset_pin.value(0)
utime.sleep(0.2)

sleep_pin.value(1)
reset_pin.value(1)
m0_pin.value(1)
m1_pin.value(1)
m2_pin.value(1)



def step(t):#hier moet een variabele meegegeven worden anders loopt hij vast: def step(t) 
    global step_pin
    step_pin.value(not step_pin.value())
 
def rotate_motor(delay):
    # Set up timer for stepping
    tim.init(freq=1000000//delay, mode=Timer.PERIODIC, callback=step)
 
def loop():
    counter = 0
    while True:
        # Set motor direction clockwise

        #dir_pin.value(randint(0,1))
        if limit0_pin.value()==1:
            dir_pin.value(0)
            utime.sleep_ms(10)
        if limit1_pin.value()==1:
            dir_pin.value(1)
            utime.sleep_ms(10)
            
            #print(limit_pin.value())
        if counter <100:
            rotate_motor(250) #hier bepaal je de stapfrequentie
            utime.sleep_ms(steps_per_revolution) #hoe lang stapt hij
            tim.deinit()  # stop the timer
            utime.sleep(1) #pauzeer 1 sec
            counter +=1
            print(counter)
        
        
        #step_pin.value(1)
        #utime.sleep_ms(1)
        #step_pin.value(0)
        #utime.sleep_ms(1)

        # Spin motor randomly
        #rotate_motor(500*randint(1,2))
        #utime.sleep_ms(int(steps_per_revolution*0.25*randint(1,4)))
        #tim.deinit()  # stop the timer
        #utime.sleep(randint(1,4)*0.03125)

        #sleep_pin.value(1)
        #utime.sleep_ms(500)
        #rotate_motor(500)
        
        #utime.sleep_ms(steps_per_revolution)
        #tim.deinit()  # stop the timer
        #utime.sleep_ms(500)
        #sleep_pin.value(0)
        #utime.sleep_ms(300)


if __name__ == '__main__':
    loop()
