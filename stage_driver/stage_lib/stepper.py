from machine import Pin
import utime


class Stepper:

    # Initializer stting the pins to control the motor andd some variables
    def __init__(self, step_pin: int, dir_pin: int, sleep_pin: int, reset_pin: int, m0: int, m1: int, m2: int):
        # Init pins from main controll
        self.step_pin = Pin(step_pin, Pin.OUT)
        self.dir_pin = Pin(dir_pin, Pin.OUT)
        self.sleep_pin = Pin(sleep_pin, Pin.OUT)
        self.reset_pin = Pin(reset_pin, Pin.OUT)
        # Pins for step size
        self.m0 = Pin(m0, Pin.OUT)
        self.m1 = Pin(m1, Pin.OUT)
        self.m2 = Pin(m2, Pin.OUT)

        # Turn of sleep mode and stop resetting
        self.sleep_pin.value(1)
        self.reset_pin.value(1)
        utime.sleep(0.2)

        # Initialize direction and position variables
        self.direction = 0
        self.delay = 1
        self.minimum_delay = 1 / 500

        # Set stepsize to full steps
        self.setStepSize(0, 0, 0)


    # Set step size of the motor
    def setStepSize(self, m0: int, m1: int, m2: int):
        self.m0.value(m0)
        self.m1.value(m1)
        self.m2.value(m2)


    # Set rotation speed by setting the delay between toggeling the step pin
    def setSpeed(self, speed: float):
        self.delay = 1 / abs(speed)
        if self.delay < self.minimum_delay:
            self.delay = self.minimum_delay
            print("Warning chosed speed to large speed set to minimum!")


    # Stop all movement
    def reset(self):
        self.reset_pin.value(0)
        utime.sleep(0.2)
        self.reset_pin.value(1)


    # Toggle sleep mode
    def sleep(self, value: int):
        if value != 0 and value != 1:
            print("Warning invalid direction choose either 1 or 0!")
            return
        self.sleep_pin.value(value)


    # Change the direction
    def setDirection(self, value: int):
        self.direction = value


    # Get the direction variable
    def getDirection(self) -> int:
        return self.direction


    # Move the stepper N times in the direction of self.direction
    def step(self, N_steps: int):
        for i in range(N_steps):
            self.step_pin.value(1)
            utime.sleep_ms(self.delay)
            self.step_pin.value(0)
            utime.sleep_ms(self.minimum_delay)




if __name__ == "__main__":

    stepper = Stepper(step_pin=14, dir_pin=15, sleep_pin=13, reset_pin=12, m0=9, m1=10, m2=11)

    print("Stepping")
    stepper.step(100)
    utime.sleep(0.5)
    print("Changing speed")
    stepper.setSpeed(500)
    print("Current direction: ", stepper.getDirection())
    print("changing direction")
    stepper.setDirection(1)
    print("Current direction: ", stepper.getDirection())
    print("Stepping")
    stepper.step(100)
    print("Changing step size")
    stepper.setStepSize(1, 1, 1)
    print("Stepping")
    stepper.step(100)
    print("Resetting")
    stepper.reset()
