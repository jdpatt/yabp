"""Base Mode."""
import logging
from abc import ABC

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
        self.serial.write(bytes([0x01]))
        version = self.serial.read(4)
        return version.decode()

    def send(self, data) -> None:
        """Write whatever is in data to the serial port."""
        self.serial.write(bytes([data]))

    def is_successful(self) -> None:
        r"""Whenever the bus pirate succesfully completes a command, it returns b"\x01"."""
        status = self.serial.read(1)
        if status != b"\x01":
            raise CommandError("Bus Pirate did not acknowledge command.")

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

    def _write_config(self) -> None:
        """Update the configuration register."""
        self.serial.write(bytes([self._config_peripherals]))
        self.is_successful()

    @property
    def config_peripherals(self) -> int:
        """Return the current configuration of the peripherals register."""
        return self._config_peripherals
