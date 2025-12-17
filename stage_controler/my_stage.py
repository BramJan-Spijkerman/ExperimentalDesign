from .dev_proto import DevProto
import csv
import os


class MyStage(DevProto):

	# Initialize super class and add callbacks
	def __init__(self, dev_id: str, port: str, save_to: str | None=None, baudrate: int=115200):
		super().__init__(dev_id, port, baudrate)

        # Register callbacks
		self.registerCallback("move_request", self.moveHandler)
		self.registerCallback("position_request", self.getPosHandler)
		self.registerCallback("reset_request", self.resetHandler)
		self.registerCallback("set_speed", self.setSpeedHandler)
		self.registerCallback("stepsize_change", self.stepSizeChangeHanddler)
		self.registerCallback("stepsize_request", self.getStepSizeHandler)

        # Set file to write to
		self.log_file = save_to
		self._create_file()
		
		# Variable to indicate stage is moving
		self.is_moving: bool = False

    # Handle move response
	def moveHandler(self, msg: dict) -> None:
		print(f"[{msg["dev_id"]}] \nreported: {msg["message"]} \ntarget position: {msg["target_position"]} \ncurrent position: {msg["current_position"]} \nstatus: {msg["status"]}\n")
		self._write_to_log(msg["target_position"], msg["current_position"])
		self.is_moving = False


    # Handle position ger response
	def getPosHandler(self, msg: dict) -> None:
		print(f"[{msg["dev_id"]}] \nreported: {msg["message"]} \ncurrent position: {msg["current_position"]} \nstatus: {msg["status"]}\n")


    # Handle reset response
	def resetHandler(self, msg: dict) -> None:
		print(f"[{msg["dev_id"]}] \nreported: {msg["message"]} \ncurrent position: {msg["current_position"]} \nstatis: {msg["status"]}\n")
		self.is_moving = False


	# Handle speed change response
	def setSpeedHandler(self, msg: dict) -> None:
		print(f"[{msg["dev_id"]}] \nreported: {msg["message"]} \nstatus: {msg["status"]}\n")


	# Handle step size change response
	def stepSizeChangeHanddler(self, msg: dict) -> None:
		print(f"[{msg["dev_id"]}] \nreported: {msg["message"]} \nstatus: {msg["status"]}\n")


	# Handle get stepsize response
	def getStepSizeHandler(self, msg: dict) -> None:
		print(f"[{msg["dev_id"]}] \nreported: {msg["message"]} \nstatus: {msg["status"]}\n")


	# Send move command
	def move(self, move: str) -> None:
		self.is_moving = True
		self.send(cmd_name="move_request", mover=move)


	# Send get position command
	def getPos(self) -> None:
		self.send(cmd_name="position_request")


	# Send reset command
	def reset(self) -> None:
		self.is_moving = True
		self.send(cmd_name="reset_request")


	# Send set speed command
	def setSpeed(self, speed: float) -> None:
		self.send(cmd_name="set_speed", speed=speed)


	# Send set step size command
	def setStepSize(self, step_size: str) -> None:
		self.send(cmd_name="stepsize_change", size=step_size)


	# Send get step size command
	def getStepSize(self) -> None:
		self.send(cmd_name="stepsize_request")


    # Write to the log file
	def _write_to_log(self, target_pos: str, actual_pos: str) -> None:
		if self.log_file:
			if not os.path.exists(self.log_file):
				raise FileNotFoundError(f"{self.log_file} does not exist!")
    
			with open(self.log_file, "r+") as file:
				file.seek(0, 2)
				writer = csv.writer(file)
				writer.writerow([target_pos, actual_pos])


    # Create the log file and write the header
	def _create_file(self) -> None:
		if self.log_file:
			with open(self.log_file, "a", newline="") as file:
				writer = csv.writer(file)
				writer.writerow(["target_pos [mm]", "actual_pos[mm]"])


	def __enter__(self):
		super().__enter__()
		return self


	def __exit__(self, exc_type, exc_val, exc_tb):
		super().__exit__(exc_type, exc_val, exc_tb)


	def __del__(self):
		super().__del__()
        
        
if __name__ == "__main__":
    Stage = MyStage("stage1", "COM4")
#         import time
        
#         stage.move("=5")
        
        # time.sleep(5)