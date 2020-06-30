"""Base Mode."""
import logging
from abc import ABC
from typing import List, Union

from yabp.decorators import check_bp_mode
from yabp.exceptions import CommandError

log = logging.getLogger("yabp")


class AbstractMode(ABC):
    """Base Mode for any of the Bus Pirate Modes."""

    def __init__(self, bp):
        self.serial = bp.serial
        self.bp = bp
        self._config_peripherals = 0x40  # Voltage and Pull-ups disabled.  AUX and CS are low.

    def version(self) -> str:
        """Return the current version of the mode."""
        self.serial.reset_input_buffer()
        self.serial.write(b"\x01")
        version = self.serial.read(4)
        return version.decode()

    def send(self, data: Union[int, List]):
        """Write whatever is in data to the serial port.

        Every mode can "bulk" transfer up to 16 bytes per command and it always expects at least
        one byte.  The command is 0b0001xxxx where the lower nibble is the number of bytes.  0b000
        means send one byte since there is no reason to send nothing.

        The Bus Pirate will reply 0x01 to the initall command and depending on the mode it will
        respond 0x00 or 0x01 to every byte.  I2C Mode an ACK is 0x00 and a NACK is 0x01. In all
        other modes the byte is just acknowledged by returning 0x01.
        """
        if isinstance(data, int):
            data = [data]
        if len(data) > 16:
            ValueError(f"Can only send 16 bytes at a time. {len(data)} was attempted.")
        elif not data:
            ValueError("List cannot be empty.  Must send at least one byte.")

        self.serial.write(bytes([0x10 | len(data) - 1]))
        self.is_successful()
        for data_to_send in data:
            self.serial.write(bytes([data_to_send]))
        return self.serial.read(len(data))

    def command(self, command: bytes):
        """Write the command to the bus pirate and make sure the command succeeded."""
        self.serial.reset_input_buffer()
        self.serial.write(command)
        self.is_successful()

    def is_successful(self) -> None:
        r"""Whenever the bus pirate successfully completes a command, it returns b"\x01"."""
        status = self.serial.read(1)
        if status != b"\x01":
            raise CommandError(f"Bus Pirate did not acknowledge command. Returned: {status}")

    @check_bp_mode
    def pullups(self, enable=False) -> None:
        """Enable or Disable the pull-ups."""
        if enable:
            self._config_peripherals |= 0x08
            log.info("Enabled Pull-ups")
        else:
            self._config_peripherals &= ~0x08
            log.info("Disabled Pull-ups")
        self._write_config()

    @check_bp_mode
    def power(self, enable=False) -> None:
        """Enable or Disable the on board power supplies."""
        if enable:
            self._config_peripherals |= 0x04
            log.info("Enabled Power Supplies")
        else:
            self._config_peripherals &= ~0x04
            log.info("Disabled Power Supplies")
        self._write_config()

    @check_bp_mode
    def set_aux_pin(self, high=True) -> None:
        """Enable or Disable the on board power supplies."""
        if high:
            self._config_peripherals |= 0x02
            log.info("Set Aux Pin High (3.3V)")
        else:
            self._config_peripherals &= ~0x02
            log.info("Set Aux Pin Low (0V)")
        self._write_config()

    @check_bp_mode
    def set_cs_pin(self, high=True) -> None:
        """Enable or Disable the on board power supplies."""
        if high:
            self._config_peripherals |= 0x01
            log.info("Set CS Pin High (3.3V)")
        else:
            self._config_peripherals &= ~0x01
            log.info("Set CS Pin Low (0V)")
        self._write_config()

    def _write_config(self) -> None:
        """Update the configuration register."""
        self.command(bytes([self._config_peripherals]))

    @property
    def config_peripherals(self) -> int:
        """Return the current configuration of the peripherals register."""
        return self._config_peripherals
