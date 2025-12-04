from machine import Pin
from math import floor
from .stepper import Stepper


class StageDriver(Stepper):

	# Iinitalize control, internal variables and default settings
	def __init__(self, dev_params: dict, step_pin: int, dir_pin: int, sleep_pin: int, reset_pin: int, m0: int, m1: int, m2: int, limit0_pin: int, limit1_pin: int):
		# Init super class
		super().__init__(step_pin, dir_pin, sleep_pin, reset_pin, m0, m1, m2)

		# Unpack device parameters
		self.id = dev_params["dev_id"]
		self.length = dev_params["length"]
		self.m = dev_params["m"]

		# Init limit switch pins
		self.limit0_pin = Pin(limit0_pin, Pin.IN, Pin.PULL_DOWN)
		self.limit1_pin = Pin(limit1_pin, Pin.IN, Pin.PULL_DOWN)

		# Init default state
		self.pos = 0
		self.setStepSize(0, 0, 0)
		self.moveToZeroPos()


	# Move the stage to the starting edge
	def moveToZeroPos(self) -> None:
		# Set correct direction
		self.setDirection(1)

		while self.readLimitSwitch(0) == 0:
			self.step(1)

		# Reverse direction and set position
		self.setDirection(0)
		self.pos = 0


	# Return the current position
	def getPos(self) -> float:
		return self.pos


	# Return device ID
	def getID(self) -> str:
		return self.id


	# Read value of selected limit switch
	def readLimitSwitch(self, switch: int) -> int | None:
		if switch == 1:
			return self.limit1_pin.value()
		elif switch == 0:
			return self.limit0_pin.value()


	# Move to entered position
	def move(self, target_pos: float) -> str | None:
		if target_pos > self.length or target_pos < 0:
			return "error", "out of bounds"

		# Determine the direction in wich to move and select limit switch
		to_move = target_pos - self.pos
		if to_move < 0:
			self.setDirection(1)
			selected_switch = 0
		if to_move > 0:
			self.setDirection(0)
			selected_switch = 1

		to_step = int(floor(to_move * self.m / self.getStepModifier()))

		# Take the required number of steps while checking the limit switch
		for i in range(abs(to_step)):
			if self.readLimitSwitch(selected_switch) == 1:
				self.pos = self.pos + 1/self.m * i * self.getStepModifier()
				return "error", "end of stage reached"

			self.step(1)

		self.pos = self.pos + 1/self.m * to_step * self.getStepModifier()
		return "ok", "moved stage"


	# Get the correct step size as float
	def getStepModifier(self) -> float:
		if self.m0.value() == 0 and self.m1.value() == 0 and self.m2.value() == 0:
			return 1
		elif self.m0.value() == 1 and self.m1.value() == 0 and self.m2.value() == 0:
			return 1/2
		elif self.m0.value() == 0 and self.m1.value() == 1 and self.m2.value() == 1:
			return 1/4
		elif self.m0.value() == 1 and self.m1.value() == 1 and self.m2.value() == 0:
			return 1/8
		else:
			return 1/16




if __name__ == "__main__":

	print("Start testing")
	dev_params = {"dev_id": "stage1",
                  "length": 320,
                  "m": 400.1}

	print("Initializing stage")
	stage = StageDriver(dev_params, step_pin=14, dir_pin=15, sleep_pin=13, reset_pin=12, m0=9, m1=10, m2=11, limit0_pin=7, limit1_pin=8)
	print("Stage moved to zero pos")
	print("Current direction: ", stage.getDirection())
	print("Current position: ", stage.getPos())
	print(f"m0 {stage.m0.value()}, m1 {stage.m1.value()}, m2 {stage.m2.value()}")
	print("Step modifier: ", stage.getStepModifier())
	print("Move to 10mm")
	stage.move(10)
	print("Current direction: ", stage.getDirection())
	print("Current position: ", stage.getPos())
	stage.move(20)
	print("Current position: ", stage.getPos())
	stage.reset()
	print("Tests completed")