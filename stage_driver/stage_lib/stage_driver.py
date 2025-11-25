from machine import Pin
from stage_lib.stepper import Stepper


class StageDriver(Stepper):

    # Initialize doing super and ading device parameters and limit switches
    def __init__(self, dev_params: dict, step_pin: int, dir_pin: int, sleep_pin: int, reset_pin: int, m0: int, m1: int, m2: int, limit0_pin: int, limit1_pin: int):
        # Initialize super class
        super().__init__(step_pin, dir_pin, sleep_pin, reset_pin, m0, m1, m2)

        # Unpack device parameters
        self.id = dev_params["stage_id"]
        self.length = dev_params["length"]
        self.m = dev_params["m"]

        # Initialize limit switch pins
        self.limit0_pin = Pin(limit0_pin, Pin.IN, Pin.PULL_DOWN)
        self.limit1_pin = Pin(limit1_pin, Pin.IN, Pin.PULL_DOWN)

        # Initialize position and move to zero
        self.pos = 0
        self.moveToZeroPos()


    # Method to move to the starting edge of the stage
    def moveToZeroPos(self):
        # Set the correct direction
        self.setDirection(1)

        while self.readLimitSwitch(0) == 0:
            self.step(1)

            if self.readLimitSwitch(0) == 1:
                self.setDirection(0)


    # Manually set the position variable
    def setPos(self, pos: float):
        if pos > self.length or pos < 0:
            print("Warning set position is out of bounds change not accepte!")
        self.pos = pos


    # Return current position
    def getPos(self) -> float:
        return self.pos


    # Read the value of selected limit switch
    def readLimitSwitch(self, switch: int):
        if switch == 1:
            return self.limit1_pin.value()
        elif switch == 0:
            return self.limit0_pin.value()
        else:
            print("Warning selected switch does not exist!")
        return None


    # Move to entered position
    def move(self, target_pos: float):
        if target_pos > self.length or target_pos < 0:
            print("Warning targeted position is out of bounds for this stage not move is made!")
            return

        m = self.m
        i = 0

        # Determine in which direction to move
        to_move = target_pos - self.pos
        if to_move < 0: self.setDirection(1)
        if to_move > 0: self.setDirection(0)

        # While target position is not reached move in that direction
        while abs(to_move) > 0:
            self.step(1)
            to_move =- m
            i =+ 1

        self.pos =+ i * m




if __name__ == "__main__":

    dev_params = {"stage_id": "stage1",
                  "length": 1,
                  "m": 1}

    print("Initializing stage")
    stage = StageDriver(dev_params, step_pin=14, dir_pin=15, sleep_pin=13, reset_pin=12, m0=9, m1=10, m2=11, limit0_pin=7, limit1_pin=8)
    print("Stage moved to zero pos")

    print("Move to 10mm")
    stage.move(10)
    print("Current direction: ", stage.getDirection())
    print("Current position: ", stage.getPos())
