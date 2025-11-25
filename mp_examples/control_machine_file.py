import time

#import serial  # TODO switch from seraial to machine
# from machine import UART, Pin #TODO switch from seraial to machine
#from enum import Enum
from machine import Pin, Timer, UART
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



#class MotorDirection(Enum):
#    TO_MOTOR = 0
#    FROM_MOTOR = 1


class MotorControlUnit():
    current_step = 0
    uart = UART(0,9600, parity=0, stop=1, bits=8, rx=Pin(1), tx=Pin(0))
    
    
    
    
    
    def main(self,runtime):
        startTime = time.time()
        
        #while True:
        while time.time() < startTime + runtime: 
            print(self.current_step)
            response = self.listen_func([("ask steps;".encode('utf-8'), "steps asked")])

            if response[0] == "steps asked":
                #print(response)
                elements = response[1].split(b";")
                send_direction = elements[1]
                send_current_step = elements[2]
                send_amount_steps = elements[3]
                self.send_response(
                    f"ask steps received;{send_direction};{str(send_current_step)};{str(send_amount_steps)};\n")

                self.do_steps(int(send_direction), int(send_current_step), int(send_amount_steps))

    def listen_func(self, listen_response_pair_list, timeout_delay_seconds=1) -> str:
        # (line_read,response)
        confirm_start_time = time.time()
        while confirm_start_time + timeout_delay_seconds > time.time():
            line_read = self.uart.readline()
            print(line_read)
            time.sleep(0.5)
            for pair in listen_response_pair_list:
                if(line_read is not None)  and (line_read.find(pair[0]) != -1):
                    print("found")
                    return pair[1], line_read

        return 'timed out'

    def do_steps(self, direction, assumed_current_steps, amount_steps):
        print(direction,assumed_current_steps,amount_steps)
        if direction == 0: #MotorDirection.TO_MOTOR
            direction_multiplier = 0  # TODO check if directions are indeed correct with motor
        else:
            direction_multiplier = 1  # TODO check if directions are indeed correct with motor
        print(f"assumed_current_steps {assumed_current_steps}")
        if assumed_current_steps == self.current_step:
            stepgoal = self.current_step * direction_multiplier * amount_steps
            self.execute_steps(amount_steps,direction_multiplier)
            #self.current_step = self.current_step + amount_steps
            stepsdoneConfirm = False
            while not stepsdoneConfirm:
                response = self.send_response("steps done;" + str(direction) + f";{self.current_step}\n",True,[(b'steps done confirmed','stepsdone')])
                if response[0] ==  'stepsdone':
                    stepsdoneConfirm = True
                else: utime.sleep_ms(10)
                    
        else:
            self.send_response(f"ERROR, STEPS NOT MATCHING, expected;{assumed_current_steps};found;{self.current_step};\n")

        # elif assumed_current_steps > current_step:

    def execute_steps(self, amount_steps, direction):
        for i in range(amount_steps):
            dir_pin.value(direction)
            utime.sleep_ms(10)
            if limit0_pin.value()==1:
                dir_pin.value(0)
                utime.sleep_ms(10)
            if limit1_pin.value()==1:
                dir_pin.value(1)
                utime.sleep_ms(10)
            
            self.rotate_motor(250) #hier bepaal je de stapfrequentie
            utime.sleep_ms(steps_per_revolution) #hoe lang stapt hij
            tim.deinit()  # stop the timer
            utime.sleep(0.5) #pauzeer 1 sec
            self.current_step=self.current_step + 1 #increment step by 1
        
    def step(self,t):#hier moet een variabele meegegeven worden anders loopt hij vast: def step(t) 
        global step_pin
        step_pin.value(not step_pin.value())
 
    def rotate_motor(self,delay):
        # Set up timer for stepping
        tim.init(freq=1000000//delay, mode=Timer.PERIODIC, callback=self.step)
    
    
    #def selfmade_rotate(self,steps):
    #    utime.sleep_us(100)
     #   for in in range(steps)
        

    def send_response(self, response_string, await_confirm=False, listen_response_pair_list=None,
                      timeout_delay_seconds=1):
        self.uart.write(response_string)
        if await_confirm:
            if listen_response_pair_list is not None:
                return self.listen_func(listen_response_pair_list, timeout_delay_seconds)


if __name__ == '__main__':
    #serial1 = serial.Serial('COM5', baudrate=9600, parity=serial.PARITY_EVEN, bytesize=8)  # open serial port
    mcu1 = MotorControlUnit()
    mcu1.main(3600)#runtime of an hour
