from dev_proto import DevProto


class MyStage(DevProto):

	# Initialize super class and add callbacks
    def __init__(self, dev_id: str, port: str, baudrate: int=115200):
        super().__init__(dev_id, port, baudrate)

        # Register callbacks
        self.registerCallback("move_request", self.moveHandler)
        self.registerCallback("position_request", self.getPosHandler)
        self.registerCallback("reset_request", self.resetHandler)
        self.registerCallback("set_speed", self.setSpeedHandler)
        self.registerCallback("stepsize_change", self.stepSizeChangeHanddler)
        self.registerCallback("stepsize_request", self.getStepSizeHandler)


    # Handle move response
    def moveHandler(self, msg: dict) -> None:
        print(f"[{msg["dev_id"]}] \nreported: {msg["message"]} \ntarget position: {msg["target_position"]} \ncurrent position: {msg["current_position"]} \nstatus: {msg["status"]}\n")


    # Handle position ger response
    def getPosHandler(self, msg: dict) -> None:
        print(f"[{msg["dev_id"]}] \nreported: {msg["message"]} \ncurrent position: {msg["current_position"]} \nstatus: {msg["status"]}\n")


    # Handle reset response
    def resetHandler(self, msg: dict) -> None:
        print(f"[{msg["dev_id"]}] \nreported: {msg["message"]} \ncurrent position: {msg["current_position"]} \nstatis: {msg["status"]}\n")


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
        self.send(cmd_name="move_request", mover=move)


	# Send get position command
    def getPos(self) -> None:
        self.send(cmd_name="position_request")


	# Send reset command
    def reset(self) -> None:
        self.send(cmd_name="reset_request")


	# Send set speed command
    def setSpeed(self, speed: float) -> None:
        self.send(cmd_name="set_speed", speed=speed)


	# Send set step size command
    def setStepSize(self, step_size: str) -> None:
        self.send(cmd_name="stepsize_change", size=step_size)


	# Send get step size command
    def getStepSize(self):
        self.send(cmd_name="stepsize_request")


    def __enter__(self):
        super().__enter__()
        return self


    def __exit__(self, exc_type, exc_val, exc_tb):
        super().__exit__(exc_type, exc_val, exc_tb)


    def __del__(self):
        super().__del__()
        
        
# if __name__ == "__main__":
#     with MyStage("stage1", "COM4") as stage:
#         import time
        
#         stage.move("=5")
        
        # time.sleep(5)