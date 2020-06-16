"""SPI Mode of the Bus Pirate."""
import logging

from yabp.decorators import check_bp_mode
from yabp.modes.abstract_mode import AbstractMode
from yabp.modes.modes import MODES

log = logging.getLogger("yabp")


class SPI(AbstractMode):
    """SPI Mode of the Bus Pirate."""

    def __init__(self, bp):
        super().__init__(bp)
        self.required_mode = MODES.SPI

        # Pin output HiZ, CKP Idle = Low, CKE Edge = Active to Idle (1), Sample Middle
        self._config_spi = 0x82

    @check_bp_mode
    def set_speed(self, speed: int = 0):
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
        if speed < 1 or speed > 10 or speed == 9:
            raise ValueError(f"{speed} is not a valid baud rate setting.")
        self.serial.write(bytes([0x60 | speed]))
        self.is_successful()

    @check_bp_mode
    def output_state(self, high=False):
        """Set the pin output to HiZ or 3.3V."""
        if high:
            self._config_spi |= 0x08
            log.info("Pin Output to 3.3V")
        else:
            self._config_spi &= ~0x08
            log.info("Pin Output to HiZ")
        self._write_config()

    @check_bp_mode
    def set_chip_select(self, high=True):
        """Set the chip select pin either high (True) or low (False)."""
        if high:
            self.serial.write(bytes([0x03]))
            log.info("Chip Select High.")
        else:
            self.serial.write(bytes([0x02]))
            log.info("Chip Select Low.")
        self.is_successful()

    @check_bp_mode
    def clock_idle_polarity(self, idle_low=True):
        """Update the clock to idle high or low."""
        if idle_low:
            self._config_spi |= 0x04
            log.info("Clock Idle High")
        else:
            self._config_spi &= ~0x04
            log.info("Clock Idle Low")
        self._write_config()

    @check_bp_mode
    def clock_edge_select(self, active_to_idle=True):
        """Update the clock to idle high or low."""
        if active_to_idle:
            self._config_spi |= 0x02
            log.info("Data transitions on active to idle clock state")
        else:
            self._config_spi &= ~0x02
            log.info("Data transitions on idle to active clock state")
        self._write_config()

    @check_bp_mode
    def sample_time(self, end=False):
        """Update the clock to idle high or low."""
        if end:
            self._config_spi |= 0x01
            log.info("Sample Data at End of Pulse.")
        else:
            self._config_spi &= ~0x01
            log.info("Sample Data at Middle of Pulse.")
        self._write_config()

    def _write_config(self):
        """Update the configuration register."""
        self.serial.write(bytes([self._config_spi]))
        self.is_successful()

    @property
    def config_spi(self):
        """Return the current configuration of the SPI register."""
        return self._config_spi
