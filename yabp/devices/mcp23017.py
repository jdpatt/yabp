import logging
from enum import Enum

import yabp

log = logging.getLogger("yabp.devices.MCP23017")


class MCP23017:
    """The Microchip MCP23017 device provides 16-bit, GPIO expansion for I2C bus applications."""

    MCP23017_MEMORYMAP = {
        "IODIRA": 0x00,
        "IODIRB": 0x01,
        "GPIOA": 0x12,
        "GPIOB": 0x13,
    }

    class DIRECTION(Enum):
        OUTPUT = 0
        INPUT = 1

    class LOGIC_LEVEL(Enum):
        LOW = 0
        HIGH = 1

    PINS = [f"A{index}" for index in range(0, 8)]
    PINS.extend([f"B{index}" for index in range(0, 8)])

    def __init__(self, seven_bit_address, bus_pirate):
        self.address = seven_bit_address
        self.i2c = bus_pirate.i2c

        self.registers = {
            "IODIRA": 0xFF,
            "IODIRB": 0xFF,
            "GPIOA": 0x00,
            "GPIOB": 0x00,
        }

    def set_direction(self, pin: str, direction: DIRECTION):
        """Update the direction of a given pin.

        The MCP23017 defaults to all pins being an input on POR.
        """
        log.debug(f"Setting {pin} to direction: {direction.name}")
        if self._is_valid_pin(pin):
            if pin[0] == "A":
                register = "IODIRA"
            else:
                register = "IODIRB"

            if direction == self.DIRECTION.INPUT:
                self._set_bit(register, int(pin[1]))
            else:
                self._clear_bit(register, int(pin[1]))

            self._write_register(register)

    def set_level(self, pin: str, logic_level: LOGIC_LEVEL):
        """Update the logic level of a given pin.

        The MCP23017 defaults to all pins being a logic low (0) on POR.
        """
        log.debug(f"Setting {pin} to logic level: {logic_level.name}")
        if self._is_valid_pin(pin):
            if pin[0] == "A":
                register = "GPIOA"
            else:
                register = "GPIOB"

            if logic_level == self.LOGIC_LEVEL.HIGH:
                self._set_bit(register, int(pin[1]))
            else:
                self._clear_bit(register, int(pin[1]))

            self._write_register(register)

    def _is_valid_pin(self, pin: str):
        """Raise an exception if the pin is invalid."""
        if pin not in self.PINS:
            raise ValueError(f"Invalid pin: {pin} for MCP23017.")
        return True

    def _set_bit(self, register, index):
        """Set the index of the bit to 1."""
        self.registers[register] |= 0x01 << index

    def _clear_bit(self, register, index):
        """Set the index of the bit to 1."""
        self.registers[register] &= ~(0x01 << index)

    def _write_register(self, register: str):
        """Write out over I2C to the device."""
        self.i2c.write_register(
            self.address, MCP23017_MEMORYMAP[register], self.registers[register]
        )

    def _read_register(self, register: str):
        """Read register from the device."""
        self.registers[register] = self.i2c.read_register(
            self.address, MCP23017_MEMORYMAP[register]
        )


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    with yabp.BusPirate() as bp:
        gpio_expander = MCP23017(0x20, bp)
        gpio_expander.set_direction("A1", gpio_expander.DIRECTION.OUTPUT)
        gpio_expander.set_level("A1", gpio_expander.LOGIC_LEVEL.HIGH)
