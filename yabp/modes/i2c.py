"""I2C Mode of the Bus Pirate."""
import logging
from typing import List, Union

from yabp.decorators import check_bp_mode
from yabp.enums import MODES
from yabp.modes.abstract_mode import AbstractMode

log = logging.getLogger("yabp")


class I2C(AbstractMode):
    """I2C Mode of the Bus Pirate."""

    def __init__(self, bp):
        super().__init__(bp)
        self.required_mode = MODES.I2C

    @check_bp_mode
    def start(self) -> None:
        """Send a start bit."""
        self.command(b"\x02")

    @check_bp_mode
    def stop(self) -> None:
        """Send a start bit."""
        self.command(b"\x03")

    @check_bp_mode
    def ack(self) -> None:
        """Acknowledge a byte."""
        self.command(b"\x06")

    @check_bp_mode
    def nack(self) -> None:
        """No Acknowledge a byte."""
        self.command(b"\x07")

    @check_bp_mode
    def read_byte(self) -> bytes:
        """Read and returns a single byte.

        You must call ack() or nack() afterwards.
        """
        self.serial.write(b"\x04")
        return self.serial.read(1)

    @check_bp_mode
    def set_speed(self, speed: int = 2) -> None:
        """Set the I2C Bus rate.

        Valid Settings: 0: 5kHz, 1: 50kHz, 2: 100Khz, 3: 400kHz
        """
        if speed < 1 or speed > 3:
            raise ValueError(f"{speed} is not a valid i2c speed setting.")
        self.command(bytes([0x60 | speed]))

    @check_bp_mode
    def write(self, address: int, data: Union[int, List]) -> None:
        """Write to an I2C device.

        This takes the 7 bit address and appends a zero (write bit) to the address.  It then
        takes data as a single value or a list of values and writes them to the device.
        """
        self.start()
        self.send(address << 1)
        if isinstance(data, int):
            # Send a single byte
            self.send(data)
        elif isinstance(data, list):
            # Send multiple bytes
            for byte_of_data in data:
                self.send(byte_of_data)
        self.stop()

    @check_bp_mode
    def read(self, address: int, number_of_bytes: int) -> str:
        """Read from an I2C device.

        This takes the 7 bit address and appends a 1 (read bit) to the address.  It then
        takes reads a `number_of_bytes` from the device.
        """
        self.start()
        self.send(address << 1 | 0x01)
        response = b""
        for _ in range(0, number_of_bytes - 1):
            response += self.read_byte()
            self.ack()
        response += self.read_byte()
        self.nack()
        self.stop()
        return response.decode()

    @check_bp_mode
    def write_register(self, address: int, register: int, data: int) -> None:
        """Write to an I2C device's register.

        This takes the 7 bit address and appends a zero (write bit) to the address.  It then
        takes data as a single value or a list of values and writes them to the device.
        """
        self.start()
        self.send(address << 1)
        self.send(register)
        self.send(data)
        self.stop()

    @check_bp_mode
    def read_register(self, address: int, register: int) -> str:
        """Read from an I2C device's register.

        This takes the 7 bit address and appends a 1 (read bit) to the address.
        """
        self.start()
        self.send(address << 1)
        self.send(register)
        self.start()
        self.send(address << 1 | 0x01)
        response = self.read_byte()
        self.nack()
        self.stop()
        return response.decode()
