"""UART Mode of the Bus Pirate."""
import logging
from typing import Union

from yabp.modes.abstract_mode import AbstractBusPirateMode

log = logging.getLogger("yabp.uart")


class UART(AbstractBusPirateMode):
    """UART Mode of the Bus Pirate."""

    def __init__(
        self, port: Union[str, None] = None, baud_rate: int = 115200, timeout: float = 0.1
    ):
        super().__init__(port, baud_rate, timeout)
        self._set_mode(b"ART1")
        self._config_uart = 0x80  # HiZ, 8/N, 1 STOP, IDLE HIGH

    def enable_rx(self, enabled: bool = False):
        """Enable passing RX data to the USB port."""
        if enabled:
            self.serial.write(b"\x03")
            log.info("Enabling UART RX")
        else:
            self.serial.write(b"\x02")
            log.info("Disabling UART RX")
        self.is_successful()

    def bridge_mode(self) -> None:
        """Start a transparent UART bridge using the current configuration.

        The only way to reset or exit is to unplug the Bus Pirate.
        """
        self.command(b"\x0F")

    def set_speed(self, speed: int = 2):
        """Set the BAUD rate for UART.

        Valid Settings:
            0: 300
            1: 1200
            2: 2400
            3: 4800
            4: 9600
            5: 19200
            6: 31250
            7: 38400
            8: 57600
            10: 115200
        """
        if speed < 1 or speed > 10 or speed == 9:
            raise ValueError(f"{speed} is not a valid baud rate setting.")
        self.command(bytes([0x60 | speed]))

    def output_state(self, high: bool = False):
        """Set the pin output to HiZ or 3.3V."""
        if high:
            self._config_uart |= 0x10
            log.info("Pin Output to 3.3V")
        else:
            self._config_uart &= ~0x10
            log.info("Pin Output to HiZ")
        self._write_config()

    def data_bits_and_parity(self, setting: int = 0):
        """Configure how many data bits and the parity of the UART.

        Valid Settings:
        0: 8/N
        1: 8/E
        2: 8/O
        3: 9/N
        """
        if setting < 0 or setting > 3:
            raise ValueError(f"{setting} is not a valid.")
        self._config_uart |= setting << 2
        self._write_config()

    def stop_bits(self, number: int):
        """Configure the number of stop bits."""
        if number == 0:
            self._config_uart |= 0x02
            log.info("One Stop Bit.")
        elif number == 1:
            self._config_uart &= ~0x02
            log.info("Two Stop Bits.")
        else:
            raise ValueError(f"{number} is not a valid.")
        self._write_config()

    def idle_polarity(self, idle_high: bool = True):
        """Update the bus to idle high or low."""
        if idle_high:
            self._config_uart |= 0x01
            log.info("Idle High")
        else:
            self._config_uart &= ~0x01
            log.info("Idle Low")
        self._write_config()

    def _write_config(self) -> None:
        """Update the configuration register."""
        self.command(bytes([self._config_uart]))

    @property
    def config_uart(self) -> int:
        """Return the current configuration of the UART register."""
        return self._config_uart
