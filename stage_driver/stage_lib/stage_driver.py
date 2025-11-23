from machine import Pin
from .stepper import Stepper


class StageDriver(Stepper):

    # Initializer
    def __init__(self, dev_params: dict, step_pin: int, dir_pin: int, m0: int, m1: int, m2: int, limit0_pin: int, limit1_pin: int):
        # Initialize Stepper super class
        super().__init__(step_pin, dir_pin, m0, m1, m2)

        # Unpackage device parameter dict to specify the delay stage
        self.id = dev_params["stage_id"]
        self.length = dev_params["length"]
        self.m = dev_params["m"]

        # Initialize limit switch pins
        self.limit0_pin = Pin(limit0_pin, Pin.IN, Pin.PULL_DOWN)
        self.limit1_pin = Pin(limit1_pin, Pin.IN, Pin.PULL_DOWN)

        # Initialize position variable and move to zero position
        self.pos = 0
        self.go_to_zero_pos()


    # Method to move to the zero position
    def go_to_zero_pos(self):
        # Set the direction of the zero position
        self.set_direction(0)

        # While direction has not changed
        while self.get_direction() == 0:

            # Advance if limit switch not pressed
            if not self.read_limit_switch(0):
                self.step_to(1)

            # Change direction and set position variable to zero if limit switch is pressed
            elif self.read_limit_switch(0):
                self.set_direction(1)
                self.set_pos(0)


    # Manually set the position varible
    def set_pos(self, pos: float):
        self.pos = pos


    # Retrun the position variable
    def get_pos(self):
        return self.pos


    # Read if the limit switch selected is pressed
    def read_limit_switch(self, selected_switch: int):
        if selected_switch == 0:
            return self.limit0_pin.value()
        if selected_switch == 1:
            return self.limit1_pin.value()


    # Method to move to some target position in mm
    def move_to_pos(self, target_pos: float):
        to_move = target_pos - self.pos

        # Determine in which direction to move
        if to_move < 0: self.set_direction(0)
        if to_move > 0: self.set_direction(1)

#        steps_to_take = self.m * abs(to_move) + self.b

        # While target position is not reached 
        while self.pos != target_pos:
            # Advance if none of the limit switched are pressed
            if not self.read_limit_switch(0) and not self.read_limit_switch(1):
                self.step_to(1)

                # Update the position variable
                if to_move < 0:
                    self.pos -= 1 / self.m
                elif to_move > 0:
                    self.pos += 1 / self.m
