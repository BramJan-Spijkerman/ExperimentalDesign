import uasyncio as asyncio
import json
import sys
import time

class USBProtocol:
    def __init__(self, heartbeat_interval=2):
        self.heartbeat_interval = heartbeat_interval
        self.command_queue = asyncio.Queue()

    # ----------------------------------------------------------
    # Checksum helpers
    # ----------------------------------------------------------
    def calc_checksum(self, s: str) -> int:
        c = 0
        for ch in s.encode():
            c ^= ch
        return c

    def verify_packet(self, packet: str) -> dict | None:
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
            sys.stdout.flush()
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

    async def process_command(self, cmd):
        if cmd.get("cmd") == "led_on":
            led_pin.value(1)
            self.send({"ok": True})

        elif cmd.get("cmd") == "led_off":
            led_pin.value(0)
            self.send({"ok": True})

        else:
            self.send({"error": "unknown_cmd", "cmd": cmd})

    # ----------------------------------------------------------
    # Start everything
    # ----------------------------------------------------------
    async def start(self):
        await asyncio.gather(
            self.read_serial(),
            self.heartbeat_task(),
            self.handle_commands()
        )

