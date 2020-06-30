"""Yet Another Bus Pirate Libray."""
import logging
from typing import Union

import serial
import serial.tools.list_ports
from yabp.decorators import requires_base_mode
from yabp.enums import MODES
from yabp.exceptions import CommandError
from yabp.modes import I2C, SPI, UART

log = logging.getLogger("yabp")


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
        self.serial.close()

    def command(self, command: bytes):
        """Write the command to the bus pirate and make sure the command succeeded."""
        self.serial.write(command)
        self.is_successful()

    def is_alive(self) -> bool:
        """Return the serial port."""
        return self.serial.is_open

    def is_successful(self) -> None:
        r"""Whenever the bus pirate succesfully completes a command, it returns b"\x01"."""
        status = self.serial.read(1)
        if status != b"\x01":
            raise CommandError(f"Bus Pirate did not acknowledge command. Returned: {status}")

    def set_mode(self, mode: MODES) -> None:
        """Change the mode of the bus pirate."""
        if self.current_mode != mode:
            self.exit_mode()
            new_mode = self._MODE_COMMANDS[mode.value]
            self.serial.reset_input_buffer()
            self.serial.write(new_mode["command"])
            returned_name = self.serial.read(len(new_mode["name"]))
            if new_mode["name"] == returned_name:
                log.info(f"Entered {mode.name} Mode.")
                self.current_mode = mode
                self.serial.reset_input_buffer()
            else:
                CommandError("Failed to change modes.")

    def exit_mode(self) -> None:
        """Leave the current mode and return to BBIO."""
        if self.current_mode != MODES.BASE:
            base_mode = self._MODE_COMMANDS[MODES.BASE.value]
            self.serial.reset_input_buffer()
            self.serial.write(base_mode["command"])
            returned_name = self.serial.read(len(base_mode["name"]))
            if base_mode["name"] == returned_name:
                self.current_mode = MODES.BASE
                self.serial.reset_input_buffer()
            else:
                CommandError("Failed to exit mode.")

    @requires_base_mode
    def reset(self) -> None:
        """Reset the Bus Pirate to the normal terminal interface.

        Send 0x0F to exit raw bitbang mode and reset the Bus Pirate.  The bp will response 0x01 on
        success.
        """
        self.command(b"\x0f")
        self.serial.reset_input_buffer()

    @requires_base_mode
    def disable_pwm(self) -> None:
        """Clear and Disable the pwm configuration."""
        self.command(b"\x13")

    @requires_base_mode
    def configure_pwm(self, period: int, duty_cycle: float, prescaler: int = 0) -> None:
        """Configure the PWM on the bus pirate's AUX pin.

        Args:
        ----
            period: pwm period in miliseconds (1e-3 == 0.1msec)
            duty_cycle: 0 to 1 (.5 == 50% Duty Cycle)
            prescaler: 0: x1, 1: x8, 2: x64, 3: x256

        """
        crystal_frequency = 32_000_000  # 32 MHz

        system_clock = 2.0 / crystal_frequency
        period_register = period / (system_clock * prescaler)
        period_register = period_register - 1
        output_compare_register = period_register * duty_cycle

        self.command(
            bytes(
                [
                    0x12,  # Setup PWM Command
                    prescaler,  # Config Byte 1
                    ((int(output_compare_register) >> 8) & 0xFF),  # Config Byte 2
                    (int(output_compare_register) & 0xFF),  # Config Byte 3
                    ((int(period_register) >> 8) & 0xFF),  # Config Byte 4
                    (int(period_register) & 0xFF),  # Config Byte 5
                ]
            )
        )


def get_serial_port() -> str:
    """Find a virtual COM port that looks like a bus pirate.

    The bus pirate v3 has a vendor id of 0403 and the documentation of the v4 lists 04D8 as the id.
    """
    potential_ports = serial.tools.list_ports.comports(include_links=True)
    for port in potential_ports:
        if any(vid in port.hwid for vid in ["0403", "04D8"]):
            return port.device
    raise ConnectionError("Failed to find Bus Pirate")
