from enum import IntEnum
import logging

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

    class DIRECTION(IntEnum):
        OUTPUT = 0
        INPUT = 1

    class LOGIC_LEVEL(IntEnum):
        LOW = 0
        HIGH = 1

    PORTA_PINS = [{f"A{index}": index} for index in range(0, 8)]
    PORTB_PINS = [{f"B{index}": index} for index in range(0, 8)]

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
        if self._valid_pin(pin):
            pass

    def set_level(self, pin: str, logic_level: LOGIC_LEVEL):
        """Update the logic level of a given pin.

        The MCP23017 defaults to all pins being a logic low (0) on POR.
        """
        log.debug(f"Setting {pin} to logic level: {logic_level.name}")
        if self._valid_pin(pin):
            pass

    def _valid_pin(self, pin: str):
        """Raise an exception if the pin is invalid."""
        if pin not in self.PORTA_PINS or pin not in self.PORTB_PINS:
            raise ValueError(f"Invalid pin: {pin} for MCP23017.")

    def _write_register(self, register: str, value: int):
        """Write out over I2C to the device."""
        self.i2c.write_register(self.address, MCP23017_MEMORYMAP[register], value)

    def _read_register(self, register: str, value: int):
        """Read register from the device."""
        return self.i2c.read_register(self.address, MCP23017_MEMORYMAP[register])


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    with yabp.BusPirate() as bp:
        gpio_expander = MCP23017(0x20, bp)
        gpio_expander.set_direction("A1", gpio_expander.DIRECTION.OUTPUT)
        gpio_expander.set_level("A1", gpio_expander.LOGIC_LEVEL.HIGH)
