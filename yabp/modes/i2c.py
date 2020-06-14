"""I2C Mode of the Bus Pirate."""
import logging
from typing import List, Union

from yabp.decorators import check_mode
from yabp.exceptions import CommandError, DeviceError
from yabp.modes.abstract_mode import AbstractMode
from yabp.modes.modes import MODES

log = logging.getLogger("Bus Pirate")


class I2C(AbstractMode):
    """I2C Mode of the Bus Pirate."""

    def __init__(self, bp):
        super().__init__(bp)
        self.required_mode = MODES.I2C
        self.config = 0x40  # Voltage and Pull-ups disabled.  AUX and CS are low.

    @check_mode
    def start(self):
        """Send a start bit."""
        self.serial.write(bytes([0x02]))
        log.debug("start")
        if not self.is_success():
            raise CommandError("Failed to send start bit correctly.")

    @check_mode
    def stop(self):
        """Send a start bit."""
        self.serial.write(bytes([0x03]))
        log.debug("stop")
        if not self.is_success():
            raise CommandError("Failed to send stop bit correctly.")

    @check_mode
    def ack(self):
        """Acknowledge a byte."""
        self.serial.write(bytes([0x06]))
        log.debug("ack")
        if not self.is_success():
            raise CommandError("Failed to send ack correctly.")

    @check_mode
    def nack(self):
        """No Acknowledge a byte."""
        self.serial.write(bytes([0x07]))
        log.debug("nack")
        if not self.is_success():
            raise CommandError("Failed to send nack correctly.")

    def check_ack(self):
        """Make sure the device acknowledged us."""
        self.read_byte()
        if not self.is_success():
            raise DeviceError("Device failed to ack.")

    @check_mode
    def read_byte(self):
        """Read and returns a single byte.

        You must call ack() or nack() afterwards.
        """
        self.serial.write(bytes([0x04]))
        return self.serial.read(1)

    @check_mode
    def pullups(self, enable=False):
        """Enable or Disable the pull-ups."""
        if enable:
            self.config = self.config | 0x08
            log.info("Enabled Pull-ups")
        else:
            self.config = self.config & ~0x08
            log.info("Disabled Pull-ups")
        self._write_config()

    @check_mode
    def power(self, enable=False):
        """Enable or Disable the on board power supplies."""
        if enable:
            self.config = self.config | 0x04
            log.info("Enabled Power Supplies")
        else:
            self.config = self.config & ~0x04
            log.info("Disabled Power Supplies")
        self._write_config()

    def _write_config(self):
        """Update the configuration register."""
        self.serial.write(bytes([self.config]))
        if not self.is_success():
            raise CommandError("Failed to update the configuration register.")

    @check_mode
    def set_speed(self, speed: int = 2):
        """Set the I2C Bus rate.

        Valid Settings: 0: 5kHz, 1: 50kHz, 2: 100Khz, 3: 400kHz
        """
        if speed < 1 or speed > 3:
            raise ValueError(f"{speed} is not a valid i2c speed setting.")
        self.serial.write(bytes([0x60 | speed]))
        if not self.is_success():
            raise CommandError("Failed to set bus speed correctly.")

    @check_mode
    def write(self, address: int, data: Union[int, List]):
        """Write to an I2C device.

        This takes the 7 bit address and appends a zero (write bit) to the address.  It then
        takes data as a single value or a list of values and writes them to the device.
        """
        self.start()
        self.send(address << 1)
        self.check_ack()
        if isinstance(data, int):
            # Send a single byte
            self.send(data)
            self.check_ack()
        elif isinstance(data, list):
            # Send multiple bytes
            for byte_of_data in data:
                self.send(data)
                self.check_ack()
        self.stop()

    @check_mode
    def read(self, address: int, number_of_bytes: int):
        """Read from an I2C device.

        This takes the 7 bit address and appends a 1 (read bit) to the address.  It then
        takes reads a `number_of_bytes` from the device.
        """
        self.start()
        self.send(address << 1 | 0x01)
        self.check_ack()
        response = ""
        for _ in range(0, number_of_bytes - 1):
            response += self.read_byte()
            self.ack()
        response += self.read_byte()
        self.nack()
        self.stop()

    @check_mode
    def write_register(self, address: int, register: int, data: int):
        """Write to an I2C device's register.

        This takes the 7 bit address and appends a zero (write bit) to the address.  It then
        takes data as a single value or a list of values and writes them to the device.
        """
        self.start()
        self.send(address << 1)
        self.check_ack()
        self.send(register)
        self.check_ack()
        self.send(data)
        self.check_ack()
        self.stop()

    @check_mode
    def read_register(self, address: int, register: int):
        """Read from an I2C device's register.

        This takes the 7 bit address and appends a 1 (read bit) to the address.
        """
        self.start()
        self.send(address << 1)
        self.check_ack()
        self.send(register)
        self.check_ack()
        self.start()
        self.send(address << 1 | 0x01)
        self.check_ack()
        self.read_byte()
        self.nack()
        self.stop()
