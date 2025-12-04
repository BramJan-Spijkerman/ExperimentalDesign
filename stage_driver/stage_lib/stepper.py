from machine import Pin
import utime

class Stepper:

	# Initialize control, internal variables and default settings
	def __init__(self, step_pin: int, dir_pin: int, sleep_pin: int, reset_pin: int, m0: int, m1: int, m2: int):
		# Init main control pins
		self.step_pin = Pin(step_pin, Pin.OUT)
		self.dir_pin = Pin(dir_pin, Pin.OUT)
		self.sleep_pin = Pin(sleep_pin, Pin.OUT)
		self.reset_pin = Pin(reset_pin, Pin.OUT)

		# Init step size pins
		self.m0 = Pin(m0, Pin.OUT)
		self.m1 = Pin(m1, Pin.OUT)
		self.m2 = Pin(m2, Pin.OUT)

		# Prevent sleep and reset mode
		self.sleep_pin.value(1)
		self.reset_pin.value(1)
		utime.sleep(0.2)	# Wait for operation to complete

		# Init default direction, delay and minimum values
		self.direction = 0
		self.delay = 1
		self.minimum_delay = 1

		# Set step size to full steps
		self.setStepSize(0, 0, 0)


	# Set motor step size
	def setStepSize(self, m0: int, m1: int, m2: int) -> None:
		self.m0.value(m0)
		self.m1.value(m1)
		self.m2.value(m2)


	# Set rotation speed
	def setSpeed(self, speed: float) -> str:
		delay = 1/abs(speed)
		if delay < self.minimum_delay:
			self.delay = self.minimum_delay
			return "error", "speed to large"
		else:
			self.delay = delay
			return "ok", f"speed set to: {speed}"


	# Reset the stepper driver
	def reset(self) -> None:
		self.reset_pin.value(0)
		utime.sleep(0.5)
		self.reset_pin.value(1)


	# Set the stepper driver to sleep mode
	def sleep(self, value: int) -> None:
		self.sleep_pin.value(value)


	# Set stepper direction
	def setDirection(self, value: int) -> str | None:
		if value != 0 and value != 1:
			return "invalid direction"

		self.direction = value
		self.dir_pin.value(value)


	# Get the direction variable
	def getDirection(self) -> int:
		return self.direction


	# Move the stepper N time
	def step(self, N_steps: int) -> None:
		for i in range(N_steps):
			self.step_pin.value(1)
			utime.sleep_ms(self.delay)
			self.step_pin.value(0)
			utime.sleep_ms(self.minimum_delay)



# Test stepper
if __name__ == "__main__":

	print("\nStarting tests\n")
	stepper = Stepper(step_pin=14, dir_pin=15, sleep_pin=13, reset_pin=12, m0=9, m1=10, m2=11)

	direction = stepper.getDirection()
	print("Current direction: {direction}")
	print("Stepping 1000 steps")
	stepper.step(1000)
	print("Changing direction")
	stepper.setDirection(1)
	print(f"Current direction: {stepper.getDirection()}")
	print("Stepping 1000 steps")
	stepper.step(1000)
	print("Changing step size")
	stepper.setStepSize(1, 0, 0)
	print("Stepping 1000 steps")
	stepper.step(1000)
	print("Changing speed")
	stepper.setSpeed(10)
	print("Stepping 1000 steps")
	stepper.step(1000)

	print("\nTests ended\n")