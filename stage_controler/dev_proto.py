import serial
import json
import threading
import time


class DevProto:

	# Initialize id, serial connection, recieve thread and callbacks
	def __init__(self, dev_id: str, port: str, baudrate: int=115200):
		self.ser = serial.Serial(port, baudrate, timeout=1)
		self.lock = threading.Lock()
		self.callbacks =  {}
		self.running = True

		# Start reciever thread
		self.recv_thread = threading.Thread(target=self._recv_loop, daemon=True)
		self.recv_thread.start()

		# Register default callbacks
		self.registerCallback("heartbeat", self.heartbeatHandler)
		self.registerCallback("ok", self.okHandler)


	# Send commands
	def send(self, cmd_name, **kwargs) -> None:
		cmd = {"cmd": cmd_name, **kwargs}

		data = json.dumps(cmd)
		chk = 0
		for b in data.encode():
			chk ^= b
		packet = data + "*" + str(chk) + "\n"
		with  self.lock:
			self.ser.write(packet.encode())


	# Register callback
	def registerCallback(self, msg_type: str, callback) -> None:
		self.callbacks[msg_type] = callback


	# Recieve loop
	def _recv_loop(self) -> None:
		buf = ""
		while self.running:
			try:
				chunk = self.ser.read(64).decode(errors="ignore")
				if chunk:
					buf += chunk
					while "\n" in buf:
						line, buf = buf.split("\n", 1)
						self._process_line(line.strip())
					else:
						time.sleep(0.01)
			except Exception as e:
					print("Recv error: ", e)


	# Process a line and call corresponding callback
	def _process_line(self, line) -> None:
		if "*" not in line:
			return
		try:
			data_str, chk_str = line.rsplit("*", 1)
			chk = int(chk_str)
			calc = 0
			for b in data_str.encode():
				calc ^= b
			if chk != calc:
				print("bad checksum: ", line)
				return
			msg = json.loads(data_str)
			msg_type = msg.get("type") or "ok"

			if msg_type in self.callbacks:
				self.callbacks[msg_type](msg)
			else:
				print("Recieved: ", msg)
		except Exception as e:
			print("Process line error: ", e)


	# Close serial connection
	def close(self) -> None:
		self.running = False
		self.recv_thread.join()
		self.ser.close()


	# Heartbeat handler
	def heartbeatHandler(self,  msg) -> None:
		print("Heartbeat: ", msg)


	# Ok handler
	def okHandler(self, msg) -> None:
		print("Response:", msg)


	def __enter__(self):
		return self


	def __exit__(self, exc_type, exc_val, axc_tb):
		return self.close()


	def __del__(self):
		return self.close()


if __name__ == "__main__":
    dev = DevProto(dev_id="LED", port="COM4")

    
    dev.send("led_on")
    time.sleep(1)
    dev.send("led_off")
    time.sleep(1)

    dev.close()
