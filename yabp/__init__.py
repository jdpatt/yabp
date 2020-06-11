"""Yet Another Bus Pirate Libray"""
import logging

from .yabp import BusPirate

__author__ = "David Patterson"
__version__ = "0.1.0"

logging.getLogger("Bus Pirate").addHandler(logging.NullHandler())
