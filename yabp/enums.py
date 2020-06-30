"""Supported Modes in yabp."""
from enum import Enum


class MODES(Enum):
    """Modes supported by yabp."""

    BASE = 0
    SPI = 1
    I2C = 2
    UART = 3
    # ONE_WIRE = 4
    # RAW_WIRE = 5
