from machine import UART, Pin


class PicoSerialHandler:

    def __init__(self, baudrate: int, tx_pin: int, rx_pin: int):
        self.uart = UART(0, baudrate, tx=Pin(tx_pin), rx=Pin(rx_pin))
