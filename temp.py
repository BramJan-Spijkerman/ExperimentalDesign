##################################################################################################################
# PC side
##################################################################################################################
import serial
import json
import threading
import time

class PicoUSBClient:
    def __init__(self, port, baud=115200):
        self.ser = serial.Serial(port, baud, timeout=0.1)
        self.lock = threading.Lock()
        self.callbacks = {}
        self.running = True

        # Start the receiver thread
        self.recv_thread = threading.Thread(target=self._recv_loop, daemon=True)
        self.recv_thread.start()

    # -----------------------
    # Send command
    # -----------------------
    def send_cmd(self, cmd_name, **kwargs):
        cmd = {"cmd": cmd_name, **kwargs}
        data = json.dumps(cmd)
        chk = 0
        for b in data.encode():
            chk ^= b
        packet = f"{data}*{chk}\n"
        with self.lock:
            self.ser.write(packet.encode())

    # -----------------------
    # Register callback for incoming messages
    # -----------------------
    def on_message(self, msg_type, callback):
        """
        msg_type: str, e.g. "heartbeat" or "ok"
        callback: function(msg_dict)
        """
        self.callbacks[msg_type] = callback

    # -----------------------
    # Receive loop
    # -----------------------
    def _recv_loop(self):
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
                print("Recv error:", e)

    def _process_line(self, line):
        if "*" not in line:
            return
        try:
            data_str, chk_str = line.rsplit("*", 1)
            chk = int(chk_str)
            calc = 0
            for b in data_str.encode():
                calc ^= b
            if chk != calc:
                print("Bad checksum:", line)
                return
            msg = json.loads(data_str)
            msg_type = msg.get("type") or "ok"  # default "ok"
            if msg_type in self.callbacks:
                self.callbacks[msg_type](msg)
            else:
                print("Received:", msg)
        except Exception as e:
            print("Process line error:", e)

    # -----------------------
    # Stop
    # -----------------------
    def close(self):
        self.running = False
        self.recv_thread.join()
        self.ser.close()


# -----------------------
# Example usage
# -----------------------
if __name__ == "__main__":
    def heartbeat_handler(msg):
        print("Heartbeat:", msg)

    def ok_handler(msg):
        print("Response:", msg)

    pico = PicoUSBClient(port="/dev/ttyACM0")  # replace with your port
    pico.on_message("heartbeat", heartbeat_handler)
    pico.on_message("ok", ok_handler)

    # Test commands
    pico.send_cmd("led_on")
    time.sleep(1)
    pico.send_cmd("led_off")
    time.sleep(1)

    pico.close()


##################################################################################################################
#Pico side
##################################################################################################################
import uasyncio as asyncio
import json
import sys
import time
import select

class SimpleQueue:
    def __init__(self):
        self.items = []

    async def put(self, item):
        self.items.append(item)

    async def get(self):
        while not self.items:
            await asyncio.sleep(0.01)
        return self.items.pop(0)


class USBProtocol:
    def __init__(self, heartbeat_interval=2):
        self.heartbeat_interval = heartbeat_interval
        self.command_queue = SimpleQueue()
        self.handlers = {}   # <-- command registry

    # ----------------------------------------------------------
    # Command registration
    # ----------------------------------------------------------
    def register(self, name: str, func):
        """Register a command handler."""
        self.handlers[name] = func

    # ----------------------------------------------------------
    # Checksum helpers
    # ----------------------------------------------------------
    def calc_checksum(self, s: str) -> int:
        c = 0
        for ch in s.encode():
            c ^= ch
        return c

    def verify_packet(self, packet: str):
        try:
            data, checksum_str = packet.rsplit("*", 1)
            checksum = int(checksum_str)
            if checksum != self.calc_checksum(data):
                return None
            return json.loads(data)
        except Exception:
            return None

    # ----------------------------------------------------------
    # Async reader for USB serial
    # ----------------------------------------------------------
    async def read_serial(self):
        buf = ""
        while True:
            if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                ch = sys.stdin.read(1)
                if ch == "\n":
                    packet = buf.strip()
                    buf = ""
                    msg = self.verify_packet(packet)
                    if msg:
                        await self.command_queue.put(msg)
                    else:
                        self.send({"error": "bad_checksum"})
                else:
                    buf += ch

            await asyncio.sleep(0.01)

    # ----------------------------------------------------------
    # Send JSON packets with checksum
    # ----------------------------------------------------------
    def send(self, obj):
        try:
            data = json.dumps(obj)
            chk = self.calc_checksum(data)
            sys.stdout.write(data + "*" + str(chk) + "\n")
            #sys.stdout.flush()
        except Exception as e:
            sys.stdout.write(json.dumps({"error": str(e)}) + "\n")
            sys.stdout.flush()

    # ----------------------------------------------------------
    # Outgoing heartbeat
    # ----------------------------------------------------------
    async def heartbeat_task(self):
        while True:
            self.send({"type": "heartbeat", "ts": time.time()})
            await asyncio.sleep(self.heartbeat_interval)

    # ----------------------------------------------------------
    # Command processor
    # ----------------------------------------------------------
    async def handle_commands(self):
        while True:
            cmd = await self.command_queue.get()
            await self.process_command(cmd)

    async def process_command(self, cmd: dict):
        name = cmd.get("cmd")

        if name in self.handlers:
            try:
                await self.handlers[name](cmd, self)
            except Exception as e:
                self.send({"error": "handler_exception", "message": str(e)})
        else:
            self.send({"error": "unknown_cmd", "cmd": name})

    # ----------------------------------------------------------
    # Start everything
    # ----------------------------------------------------------
    async def start(self):
        await asyncio.gather(
            self.read_serial(),
            self.heartbeat_task(),
            self.handle_commands()
        )

##################################################################################################################
##################################################################################################################
##################################################################################################################
from pico_serial_handler import USBProtocol
import uasyncio as asyncio
from machine import Pin

led_pin = Pin(25, Pin.OUT)

async def led_on(cmd, proto):
    led_pin.value(1)
    proto.send({"ok": True})

async def led_off(cmd, proto):
    led_pin.value(0)
    proto.send({"ok": True})

proto = USBProtocol()

proto.register("led_on", led_on)
proto.register("led_off", led_off)

asyncio.run(proto.start())

