"""Supported Modes in yabp."""
from enum import Enum


class MODES(Enum):
    """Modes supported by yabp."""

    BASE = 1
    SPI = 2
    I2C = 3
    UART = 4
    ONE_WIRE = 5
    RAW_WIRE = 6
