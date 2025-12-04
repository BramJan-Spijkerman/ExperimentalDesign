import uasyncio as asyncio
import json
import sys
import time
import select



# Class to implement a task queue
class SimpleQueue:

	# Initialize the task list
	def __init__(self):
		self.items = []


	# Append onto the queue
	async def put(self, item: Callable[dict, Proto]) -> None:
		self.items.append(item)


	# Get items from the queue
	async def get(self) -> Callable[dict, Proto]:
		while not self.items:
			await asyncio.sleep(0.01)
		return self.items.pop(0)



# Class to hande the async serial communication
class Proto:

	# Initialize default settings and create the task queue
	def __init__(self, heartbeat_interval: int=2, send_heartbeat: bool=False):
		self.send_heartbeat = send_heartbeat
		self.heartbeat_interval = heartbeat_interval
		self.command_queue = SimpleQueue()
		self.handlers = {}


	# Command registry
	def register(self, name: str, func) -> None:
		self.handlers[name] = func


	# Calculate checksum
	def calcChecksum(self, s: str) -> int:
		c = 0
		for ch in s.encode():
			c ^= ch
		return c


	# Verify checksum
	def verifyPacket(self, packet: str) -> dict | None:

		try:
			data, checksum_str = packet.rsplit("*", 1)
			checksum = int(checksum_str)

			if checksum != self.calcChecksum(data):
				return None

			return json.loads(data)
		except Exception:
			return None


	# Async serial reader
	async def readSerial(self) -> None:
		buf = ""

		while True:
			if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
				ch = sys.stdin.read(1)
				if ch == "\n":
					packet = buf.strip()
					buf = ""
					msg = self.verifyPacket(packet)
					if msg:
						await self.command_queue.put(msg)
					else:
						self.send({"error": "bad_checksum"})
				else:
					buf += ch

			await asyncio.sleep(0.01)


	# Send JSON packet with checksum
	def send(self, obj: str) -> None:
		try:
			data = json.dumps(obj)
			chk = self.calcChecksum(data)
			sys.stdout.write(data + "*" + str(chk) + "\n")
		except Exception as e:
			data = json.dumps({"error": str(e)})
			chk = self.calcChecksum(data)
			sys.stdout.write(data + "*" + str(chk) + "\n")


	# Outgoing heartbeat
	async def hearbeatTask(self) -> None:
		if self.send_heartbeat == True:
			while True:
				self.send({"type": "heartbeat", "ts": time.time()})
				await asyncio.sleep(self.heartbeat_interval)


	# Command processor
	async def handleCommands(self) -> None:
		while True:
			cmd = await self.command_queue.get()
			await self.processCommand(cmd)


	async def processCommand(self, cmd: dict) -> None:
		name = cmd.get("cmd")

		if name in self.handlers:
			try:
				await self.handlers[name](cmd, self)
			except Exception as e:
				self.send({"error": "handler_exception", "message": str(e)})
		else:
			self.send({"error": "unknown_cmd", "cmd": name})


	# Start the whole thing
	async def start(self) -> None:
		await asyncio.gather(
			self.readSerial(),
			self.hearbeatTask(),
			self.handleCommands()
			)




# MAIN PROGRAM
if __name__ == "__main__":
	from stage_lib.stage_driver import StageDriver

	# Define the particulates of the delay stage
	dev_params = {"dev_id": "stage1",
                  "length": 210,
                  "m": 400.1}

    # Instantiate the stage and USB protocol classes
	proto = Proto(2)
	stage = StageDriver(dev_params, step_pin=14, dir_pin=15, sleep_pin=13, reset_pin=12, m0=9, m1=10, m2=11, limit0_pin=7, limit1_pin=8)


    # Expose stage driver commands to the USB port
    # Move command
	async def move(cmd: dict, proto: Proto) -> None:

    	# Parse move type
		if cmd["mover"][0] == "=":
			target_position = float(cmd["mover"][1:])
		elif cmd["mover"][0] == "+":
			target_position = stage.getPos() + float(cmd["mover"][1:])
		elif cmd["mover"][0] == "-":
			target_position = stage.getPos() - float(cmd["mover"][1:])
		else:
			message = "invalid positioning operator"
			status = "error"

		status, message =  stage.move(target_position)

		proto.send({"dev_id": stage.getID(),
    				"message": message,
    				"target_position": target_position,
    				"current_position": stage.getPos(),
    				"status": status,
    				"type": "move_request"})


    # Request position command
	async def getPos(cmd: dict, proto: Proto) -> None:
		proto.send({"dev_id": stage.getID(),
    				"message": "requested stage position",
    				"current_position": stage.getPos(),
    				"status": "ok",
    				"type": "position_request"})


    # Reset command
	async def reset(cmd: dict, proto: Proto) -> None:
		stage.moveToZeroPos()
		stage.reset()

		proto.send({"dev_id": stage.getID(),
    				"message": "requested reset",
    				"current_position": stage.getPos(),
    				"status": "ok",
    				"type": "reset_request"})


    # Set speed command
	async def setSpeed(cmd: dict, proto: Proto) -> None:
		status, message = stage.setSpeed(cmd["speed"])

		proto.send({"dev_id": stage.getID(),
    				"message": message,
    				"status": status,
    				"type": "set_speed"})


    # Set step size command
	async def setStepSize(cmd: dict, proto: Proto) -> None:
		size = cmd["size"]
		status = "ok"
		m0, m1, m2 = 0, 0, 0
		if size == "1":
			message = "changed step size to full steps"
		elif size == "1/2":
			m0, m1, m2 = 1, 0, 0
			message = "changed step size to half steps"
		elif size == "1/4":
			m0, m1, m2 = 0, 1, 0
			message = "changed step size to quarter steps"
		elif size == "1/8":
			m0, m1, m2 = 1, 1, 0
			message = "changed step size to eight steps"
		elif size == "1/16":
			m0, m1, m2 = 1, 1, 1
			message = "changed step size to sixteenth steps"
		else:
			status = "error"
			message = "invalid step size requested set to full steps"

		stage.setStepSize(m0, m1, m2)

		proto.send({"dev_id": stage.getID(),
					"message": message,
					"status": status,
					"type": "stepsize_change"})


    # get step size command
	async def getStepSize(cmd: dict, proto: Proto) -> None:
		size = stage.getStepModifier()
		if size == 1:
			size_str = "1"
		elif size == 0.5:
			size_str = "1/2"
		elif size == 0.25:
			size_str = "1/4"
		elif size == 0.0625:
			size_str = "1/16"

		proto.send({"dev_id": stage.getID(),
                    "message": size_str,
                    "status": "ok",
                    "type": "stepsize_request"})


    # Register tasks
	proto.register("move_request", move)
	proto.register("position_request", getPos)
	proto.register("reset_request", reset)
	proto.register("set_speed", setSpeed)
	proto.register("stepsize_change", setStepSize)
	proto.register("stepsize_request", getStepSize)

    # Start the event loop
	asyncio.run(proto.start())