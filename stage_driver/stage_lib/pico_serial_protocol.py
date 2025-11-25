import uasyncio as asyncio
import json
import sys
import time
import select


# Class to create a task queue
class SimpleQueue:

    # Initializer creating the task list
    def __init__(self):
        self.items = []


    # Method to append onto the queue
    async def put(self, item):
        self.items.append(item)


    # Method to get items from queue
    async def get(self):
        while not self.items:
            await asyncio.sleep(0.01)
        return self.items.pop(0)


# Class to handle the async serial communication
class USBProtocol:

    # Initializer setting the interval for heartbeat and creating the queue
    def __init__(self, heartbeat_interval=2):
        self.heartbeat_interval = heartbeat_interval
        self.command_queue = SimpleQueue()
        self.handlers = {}


    # Command registration
    def register(self, name: str, func):
        self.handlers[name] = func


    # Calculates the checksum
    def calcChecksum(self, s: str) -> int:
        c = 0
        for ch in s.encode():
            c ^= ch
        return c


    # Verify is checksum is correct
    def verifyPacket(self, packet: str):

        try:
            data, checksum_str = packet.rsplit("*", 1)
            checksum = int(checksum_str)

            if checksum != self.calcChecksum(data):
                    return None

            return json.loads(data)
        except Exception:
            return None


    # Async reader for USB port
    async def readSerial(self):
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
    def send(self, obj):
        try:
            data = json.dumps(obj)
            chk = self.calcChecksum(data)
            sys.stdout.write(data + "*" + str(chk) + "\n")
        except Exception as e:
            data = json.dumps({"error": str(e)})
            chk = self.calcChecksum(data)
            sys.stdout.write(data + "*" + str(chk) + "\n")


    # Outgoing heartbeat
    async def heartbeatTask(self):
        while True:
            self.send({"type": "heartbeat", "ts": time.time()})
            await asyncio.sleep(self.heartbeat_interval)


    # Command processor
    async def handleCommands(self):
        while True:
            cmd = await self.command_queue.get()
            await self.processCommand(cmd)


    async def processCommand(self, cmd: dict):
        name = cmd.get("cmd")

        if name in self.handlers:
            try:
                await self.handlers[name](cmd, self)
            except Exception as e:
                self.send({"error": "handler_exception", "message": str(e)})
        else:
            self.send({"error": "unknown_cmd", "cmd": name})


    # Start the whole thing
    async def start(self):
        await asyncio.gather(
            self.readSerial(),
            self.heartbeatTask(),
            self.handleCommands()
            )



if __name__ == "__main__":
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
