"""Yet Another Bus Pirate Libray."""
import logging
from enum import IntFlag, auto
from typing import Union

import serial
import serial.tools.list_ports
from yabp.decorators import requires_base_mode
from yabp.exceptions import CommandError
from yabp.modes import I2C, MODES, SPI, UART

log = logging.getLogger("yabp")


class Pins(IntFlag):
    """Each GPIO on the bus pirate that can be configured as an input or output."""

    CS = auto()
    MISO = auto()
    CLK = auto()
    MOSI = auto()
    AUX = auto()
    PULLUP = auto()
    POWER = auto()


class BusPirate:
    """Parent class for all bus pirate modes."""

    _MODE_COMMANDS = {
        MODES.BASE.value: {"name": b"BBIO1", "command": b"\x00"},
        MODES.SPI.value: {"name": b"SPI1", "command": b"\x01"},
        MODES.I2C.value: {"name": b"I2C1", "command": b"\x02"},
        MODES.UART.value: {"name": b"ART1", "command": b"\x03"},
        # MODES.ONE_WIRE.value: {"name": b"1W01", "command": b"\x04"},
        # MODES.RAW_WIRE.value: {"name": b"RAW1", "command": b"\x05"},
    }

    def __init__(
        self, port: Union[str, None] = None, baud_rate: int = 115200, timeout: float = 0.1
    ):

        self.serial: serial.Serial = self.open(port, baud_rate, timeout)
        self.current_mode = MODES.BASE

        # Initalize Mode Classes
        self.i2c = I2C(self)
        self.spi = SPI(self)
        self.uart = UART(self)

    def __enter__(self) -> "BusPirate":
        """Allow using the bus pirate as a context manager.

        Example:
        -------
        ```python
        with BusPirate("COM3") as bp:
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
        The bp will response with BBIO1 when it succeedes.
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
            serial_port.write(bytes([0x00]))
            status = serial_port.read(5)
            if b"BBIO" in status:
                serial_port.reset_input_buffer()
                return serial_port
        raise CommandError("Failed to Reset Bus Pirate.")

    def close(self) -> None:
        """Free the serial port."""
        self.serial.close()

    def is_alive(self) -> bool:
        """Return the serial port."""
        return self.serial.is_open

    def is_successful(self) -> None:
        r"""Whenever the bus pirate succesfully completes a command, it returns b"\x01"."""
        status = self.serial.read(1)
        if status != b"\x01":
            raise CommandError("Bus Pirate did not acknowledge command.")

    def set_mode(self, mode: MODES):
        """Change the mode of the bus pirate."""
        if self.current_mode != mode:
            self.exit_mode()
            new_mode = self._MODE_COMMANDS[mode.value]
            self.serial.reset_input_buffer()
            self.serial.write(new_mode["command"])
            name = self.serial.read(len(new_mode["name"]))
            if new_mode["name"] == name:
                log.info(f"Entered {mode.name} Mode.")
                self.current_mode = mode
                self.serial.reset_input_buffer()
                return
            else:
                CommandError("Failed to change modes.")

    def exit_mode(self) -> None:
        """Leave the current mode and return to BBIO."""
        if self.current_mode != MODES.BASE:
            base_mode = self._MODE_COMMANDS[MODES.BASE.value]
            self.serial.reset_input_buffer()
            self.serial.write(base_mode["command"])
            name = self.serial.read(len(base_mode["name"]))
            if base_mode["name"] == name:
                log.info(f"Left {self.current_mode.name} Mode.")
                self.current_mode = MODES.BASE
                self.serial.reset_input_buffer()
                return
            else:
                CommandError("Failed to exit mode.")

    @requires_base_mode
    def reset(self) -> None:
        """Reset the Bus Pirate to the normal terminal interface.

        Send 0x0F to exit raw bitbang mode and reset the Bus Pirate.  The bp will response 0x01 on
        success.
        """
        self.serial.write(bytes([0x0F]))
        if self.is_successful():
            log.info("Exited Scripting Mode.")
        self.serial.reset_input_buffer()


def get_serial_port() -> str:
    """Find an USB to Serial comport."""
    potential_ports = serial.tools.list_ports.comports(include_links=True)
    for port in potential_ports:
        if "usbserial" in port.device:
            return port.device
    raise ConnectionError("Failed to find Bus Pirate")
