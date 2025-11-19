from machine import Pin
import utime



class Stepper:

    # Initializer setting the pins to control the motor driver
    def __init__(self, step_pin: int, dir_pin: int, m0: int, m1: int, m2: int):
        # Initialize Pins
        self.step_pin = Pin(step_pin, Pin.OUT)
        self.dir_pin = Pin(dir_pin, Pin.OUT)
        self.m0 = Pin(m0, Pin.OUT)
        self.m1 = Pin(m1, Pin.OUT)
        self.m2 = Pin(m2, Pin.OUT)

        # Initialize direction and position variables
        self.direction = 0
        self.step_pos = 0

        # Set step size to full steps
        self.set_step_size(0, 0, 0)


    # Set step size from full steps to sixteenth steps
    def set_step_size(self, m0_val: int, m1_val: int, m2_val: int):
        self.m0.value(m0_val)
        self.m1.value(m1_val)
        self.m2.value(m2_val)


    # Set rotation speed by setting the delay between toggeling the step pin
    def set_speed(self, speed: float):
        self.delay = 1 / abs(speed)


    # Set direction by toggeling the direction pin and update the direction variable
    def set_direction(self, direction: int):
        self.dir_pin.value(direction)
        self.direction = direction


    # Get the direction variable
    def get_direction(self):
        return self.direction


    # Manually set the stepper position in units of steps from the zero position
    def set_step_pos(self, step_pos: int):
        self.step_pos = step_pos


    # Move the stepper to some step position
    def step_to(self, step_position: int):
        # calculate the number of steps to take
        to_step = step_position - self.step_pos

        # Determine in wich direction to take steps
        if to_step > 0:
            self.set_direction(1)
        elif to_step < 0:
            self.set_direction(0)

        # Start stepping until the target position is reachted
        while self.step_pos != step_position:
            self.step_pin.value(1)
            utime.sleep(self.delay)
            self.step_pin.value(0)

            # Update the position variable
            if to_step > 0:
                self.step_pos += 1
            elif to_step < 0:
                self.step_pos -= 1




