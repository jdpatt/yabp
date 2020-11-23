"""Base Mode of the Bus Pirate."""
import logging
from typing import Union

import serial

from yabp.modes.abstract_mode import AbstractBusPirateMode

log = logging.getLogger("yabp.base")


class Base(AbstractBusPirateMode):
    """Base Mode of the Bus Pirate."""

    def __init__(
        self, port: Union[str, None] = None, baud_rate: int = 115200, timeout: float = 0.1
    ):
        super().__init__()
        self.serial: serial.Serial = self.open(port, baud_rate, timeout)
        self._config_peripherals = 0x80  # POWER|PULLUP|AUX|MOSI|CLK|MISO|CS
        self._config_pin_direction = 0x5F  # AUX|MOSI|CLK|MISO|CS

    def disable_pwm(self) -> None:
        """Clear and Disable the pwm configuration."""
        self.command(b"\x13")

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

    def pullups(self, enable=False) -> None:
        """Enable or Disable the pull-ups."""
        if enable:
            self._config_peripherals |= 0x20
            log.info("Enabled Pull-ups")
        else:
            self._config_peripherals &= ~0x20
            log.info("Disabled Pull-ups")
        self._write_config()

    def power(self, enable=False) -> None:
        """Enable or Disable the on board power supplies."""
        if enable:
            self._config_peripherals |= 0x40
            log.info("Enabled Power Supplies")
        else:
            self._config_peripherals &= ~0x40
            log.info("Disabled Power Supplies")
        self._write_config()

    def set_aux_pin(self, high=True) -> None:
        """Set the aux pin high or low."""
        if high:
            self._config_peripherals |= 0x10
            log.info("Set Aux Pin High (3.3V)")
        else:
            self._config_peripherals &= ~0x10
            log.info("Set Aux Pin Low (0V)")
        self._write_config()

    def set_mosi_pin(self, high=True) -> None:
        """Set the mosi pin high or low."""
        if high:
            self._config_peripherals |= 0x08
            log.info("Set MOSI Pin High (3.3V)")
        else:
            self._config_peripherals &= ~0x08
            log.info("Set MOSI Pin Low (0V)")
        self._write_config()

    def set_miso_pin(self, high=True) -> None:
        """Set the miso pin high or low."""
        if high:
            self._config_peripherals |= 0x02
            log.info("Set MISO Pin High (3.3V)")
        else:
            self._config_peripherals &= ~0x02
            log.info("Set MISO Pin Low (0V)")
        self._write_config()

    def set_clk_pin(self, high=True) -> None:
        """Set the clk pin high or low."""
        if high:
            self._config_peripherals |= 0x04
            log.info("Set Clk Pin High (3.3V)")
        else:
            self._config_peripherals &= ~0x04
            log.info("Set Clk Pin Low (0V)")
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

    def _write_pin_direction(self) -> None:
        """Update the pin direction register.

        Register Format: (010xxxxx) AUX|MOSI|CLK|MISO|CS
        """
        self.command(bytes([self._config_pin_direction]))

    def set_aux_direction(self, output=False) -> None:
        """Set the aux pin direction to either an input (1) or output (0)."""
        if output:
            self._config_pin_direction &= ~0x10
        else:
            self._config_pin_direction |= 0x10
        self._write_pin_direction()

    def set_mosi_direction(self, output=False) -> None:
        """Set the mosi pin direction to either an input (1) or output (0)."""
        if output:
            self._config_pin_direction &= ~0x08
        else:
            self._config_pin_direction |= 0x08
        self._write_pin_direction()

    def set_miso_direction(self, output=False) -> None:
        """Set the miso pin direction to either an input (1) or output (0)."""
        if output:
            self._config_pin_direction &= ~0x02
        else:
            self._config_pin_direction |= 0x02
        self._write_pin_direction()

    def set_clk_direction(self, output=False) -> None:
        """Set the clk pin direction to either an input (1) or output (0)."""
        if output:
            self._config_pin_direction &= ~0x04
        else:
            self._config_pin_direction |= 0x04
        self._write_pin_direction()

    def set_cs_direction(self, output=False) -> None:
        """Set the cs pin direction to either an input (1) or output (0)."""
        if output:
            self._config_pin_direction &= ~0x01
        else:
            self._config_pin_direction |= 0x01
        self._write_pin_direction()
