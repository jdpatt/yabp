"""Base Mode."""
from abc import ABC


class AbstractMode(ABC):
    """Base Mode for any of the Bus Pirate Modes."""

    def __init__(self, bp):
        self.serial = bp.serial
        self.bp = bp

    def version(self):
        """Return the current version of the mode."""
        self.serial.reset_input_buffer()
        self.serial.write(bytes([0x01]))
        version = self.serial.read(4)
        return version.decode()

    def send(self, data):
        """Write whatever is in data to the serial port."""
        self.serial.write(bytes([data]))

    def is_success(self) -> bool:
        r"""Whenever the bus pirate succesfully completes a command, it returns b"\x01"."""
        status = self.serial.read(1)
        if status == b"\x01":
            return True
        return False
