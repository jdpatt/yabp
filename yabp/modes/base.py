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
        self.serial: serial.Serial = self.open(port, baud_rate, timeout)

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
