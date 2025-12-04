from numpy import array


class PIDcontroler:

	# Initialize gains, setpoint errors and integral
	def __init__(self, Kp: float, Ki: float, Kd: float, setpoint: float):
		# Init gains
		self.Kp = Kp
		self.Ki = Ki
		self.Kd = Kd

		# Setpoint
		self.setpoint = setpoint

		# Error history and integral
		self.previous_error = 0
		self.integral = 0


	def compute(self, process_variable: float, dt: float) -> float:
		# Compute error
		error = self.setpoint - process_variable

		# Compute proportional stage
		P_out  = self.Kp * error

		# Compute differential stage
		D_out = self.Kd * (self.previous_error - error) / dt

		# Compute integral stage
		self.integral += error * dt
		I_out = self.Ki * self.integral

		return P_out + D_out + I_out