"""SPI Mode of the Bus Pirate."""
import logging
from typing import Union

from yabp.modes.abstract_mode import AbstractBusPirateMode

log = logging.getLogger("yabp.spi")


class SPI(AbstractBusPirateMode):
    """SPI Mode of the Bus Pirate."""

    def __init__(
        self, port: Union[str, None] = None, baud_rate: int = 115200, timeout: float = 0.1
    ):
        super().__init__(port, baud_rate, timeout)
        self._set_mode(b"SPI1")

        # Pin output HiZ, CKP Idle = Low, CKE Edge = Active to Idle (1), Sample Middle
        self._config_spi = 0x82

    def set_speed(self, speed: int = 0) -> None:
        """Set the clock rate for SPI.

        Valid Settings:
            0: 30kHz
            1: 125kHz
            2: 250kHz
            3: 1MHz
            4: 2MHz
            5: 2.6MHz
            6: 4MHz
            7: 8MHz
        """
        if speed < 0 or speed > 7:
            raise ValueError(f"{speed} is not a valid baud rate setting.")
        self.command(bytes([0x60 | speed]))

    def output_state(self, high: bool = False) -> None:
        """Set the pin output to HiZ or 3.3V."""
        if high:
            self._config_spi |= 0x08
            log.info("Pin Output to 3.3V")
        else:
            self._config_spi &= ~0x08
            log.info("Pin Output to HiZ")
        self._write_config()

    def set_chip_select(self, high: bool = True) -> None:
        """Set the chip select pin either high (True) or low (False)."""
        if high:
            self.serial.write(b"\x03")
            log.info("Chip Select High.")
        else:
            self.serial.write(b"\x02")
            log.info("Chip Select Low.")
        self.is_successful()

    def clock_idle_polarity(self, idle_low: bool = True) -> None:
        """Update the clock to idle high or low."""
        if idle_low:
            self._config_spi |= 0x04
            log.info("Clock Idle High")
        else:
            self._config_spi &= ~0x04
            log.info("Clock Idle Low")
        self._write_config()

    def clock_edge_select(self, active_to_idle: bool = True) -> None:
        """Update the clock to idle high or low."""
        if active_to_idle:
            self._config_spi |= 0x02
            log.info("Data transitions on active to idle clock state")
        else:
            self._config_spi &= ~0x02
            log.info("Data transitions on idle to active clock state")
        self._write_config()

    def sample_time(self, end: bool = False) -> None:
        """Update the clock to idle high or low."""
        if end:
            self._config_spi |= 0x01
            log.info("Sample Data at End of Pulse.")
        else:
            self._config_spi &= ~0x01
            log.info("Sample Data at Middle of Pulse.")
        self._write_config()

    def _write_config(self) -> None:
        """Update the configuration register."""
        self.command(bytes([self._config_spi]))

    @property
    def config_spi(self) -> int:
        """Return the current configuration of the SPI register."""
        return self._config_spi
