"""Base Mode."""
import logging
from abc import ABC
from typing import List, Union

import serial
import serial.tools.list_ports

from yabp.exceptions import CommandError

log = logging.getLogger("yabp")


class AbstractBusPirateMode(ABC):
    """Base Mode for any of the Bus Pirate Modes."""

    _MODES = {
        b"BBIO1": b"\x00",
        b"SPI1": b"\x01",
        b"I2C1": b"\x02",
        b"ART1": b"\x03",
        b"1W01": b"\x04",
        b"RAW1": b"\x05",
    }

    def __init__(
        self, port: Union[str, None] = None, baud_rate: int = 115200, timeout: float = 0.1
    ):
        self.serial: serial.Serial = self.open(port, baud_rate, timeout)
        self._config_peripherals = 0x40  # Voltage and Pull-ups disabled.  AUX and CS are low.

    def __enter__(self):
        """Allow using the bus pirate as a context manager.

        Example:
        -------
        ```python
        with I2C("COM3") as bp:
            bp.is_alive()
        ```

        """
        return self

    def __exit__(self, *args):
        """Clean up from using the bus pirate as a context manager."""
        self.close()

    def open(self, port, baud_rate, timeout) -> serial.Serial:
        """Open the serial port and enter the scripting mode.

        Send 0x00 to the user terminal (max.) 20 times to enter the raw binary bitbang mode.
        The bp will response with BBIO1 when it succeeds.
        """
        try:
            if not port:
                port = get_serial_port()
            serial_port = serial.Serial(port=port, baudrate=baud_rate, timeout=timeout)
            log.info(f"Connected to Bus Pirate on {port}")
        except serial.serialutil.SerialException:
            log.error("Failed to connect to Bus Pirate.")
            raise

        serial_port.reset_input_buffer()
        for _ in range(0, 20):
            serial_port.write(b"\x00")
            status = serial_port.read(5)
            if b"BBIO" in status:
                serial_port.reset_input_buffer()
                return serial_port
        raise CommandError("Failed to Reset Bus Pirate.")

    def close(self) -> None:
        """Free the serial port."""
        self._set_mode(b"BBIO1")
        self._reset_bus_pirate()
        self.serial.close()
        log.info("Closed connection to Bus Pirate.")

    def _set_mode(self, mode: bytes) -> None:
        """Change the mode of the bus pirate."""
        self.serial.reset_input_buffer()
        self.serial.write(self._MODES[mode])
        returned_name = self.serial.read(len(mode))
        self.serial.reset_input_buffer()
        if mode != returned_name:
            CommandError("Failed to change modes.")
        log.debug("Current Mode - {}".format(mode.decode()))

    def _reset_bus_pirate(self) -> None:
        """Reset the Bus Pirate to the normal terminal interface.

        Send 0x0F to exit raw bitbang mode and reset the Bus Pirate.  The bp will response 0x01 on
        success.
        """
        self.command(b"\x0f")
        self.serial.reset_input_buffer()

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

    def is_alive(self) -> bool:
        """Return the serial port."""
        return self.serial.is_open

    def pullups(self, enable=False) -> None:
        """Enable or Disable the pull-ups."""
        if enable:
            self._config_peripherals |= 0x08
            log.info("Enabled Pull-ups")
        else:
            self._config_peripherals &= ~0x08
            log.info("Disabled Pull-ups")
        self._write_config()

    def power(self, enable=False) -> None:
        """Enable or Disable the on board power supplies."""
        if enable:
            self._config_peripherals |= 0x04
            log.info("Enabled Power Supplies")
        else:
            self._config_peripherals &= ~0x04
            log.info("Disabled Power Supplies")
        self._write_config()

    def set_aux_pin(self, high=True) -> None:
        """Set the aux pin high or low."""
        if high:
            self._config_peripherals |= 0x02
            log.info("Set Aux Pin High (3.3V)")
        else:
            self._config_peripherals &= ~0x02
            log.info("Set Aux Pin Low (0V)")
        self._write_config()

    def set_cs_pin(self, high=True) -> None:
        """Set the cs pin high or low."""
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


def get_serial_port() -> str:
    """Find a virtual COM port that looks like a bus pirate.

    The bus pirate v3 has a vendor id of 0403 and the documentation of the v4 lists 04D8 as the id.
    """
    potential_ports = serial.tools.list_ports.comports(include_links=True)
    for port in potential_ports:
        if any(vid in port.hwid for vid in ["0403", "04D8"]):
            return port.device
    raise ConnectionError("Failed to find Bus Pirate")
