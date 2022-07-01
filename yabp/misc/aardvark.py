"""Add support to use the aardvark with the same interface as the bus pirate.

Different pieces equipment are available in the lab at different times.
"""
import logging
from typing import List

try:
    from aardvark_py import (
        AA_CONFIG_SPI_I2C,
        AA_I2C_NO_FLAGS,
        AA_I2C_NO_STOP,
        aa_close,
        aa_configure,
        aa_find_devices_ext,
        aa_i2c_bitrate,
        aa_i2c_read,
        aa_i2c_write,
        aa_open,
        aa_status_string,
        array,
    )
except ModuleNotFoundError as error:
    print("ERROR: Did you copy over the total phase files?")
    raise


class I2C:
    """Shim around the Total Phase python API to use it like a bus pirate.

    Ensure that you copy aardvark_py.py and aardvark.dll/.so from the api download
    to this folder or the import above will fail.
    """

    def __init__(self):
        self.log = logging.getLogger("i2c")

        _, ports, _ = aa_find_devices_ext(16, 16)
        self.port = ports[0]  # Use the first one found.
        self.aardvark = aa_open(self.port)
        if self.aardvark <= 0:
            error_message = "Failed to connect to aardvark."
            self.log.error(error_message)
            raise ConnectionError(error_message)

        self._set_mode()

    def __enter__(self):
        """Allow using the bus pirate as a context manager.

        Example:
        -------
            ```python
            with I2C("COM3") as aardvark:
                aardvark.read(...)
            ```

        """
        return self

    def __exit__(self, *args):
        """Clean up from using the Aardvark as a context manager."""
        self.close()

    def close(self) -> None:
        """Free the serial port."""
        aa_close(self.aardvark)
        self.log.info("Closed connection to Aardvark.")

    def _set_mode(self, bitrate: int = 100) -> None:
        """Ensure that the I2C subsystem is enabled.

        Args:
        ----
            bitrate: Sets the bus speed for i2c. Default is 100kHz.

        """
        aa_configure(self.aardvark, AA_CONFIG_SPI_I2C)
        self.bitrate = aa_i2c_bitrate(self.aardvark, bitrate)

    def write_register(self, address: int, register: int, data: int) -> None:
        """Write to an I2C device's register."""
        aa_i2c_write(self.aardvark, address, AA_I2C_NO_STOP, array("B", [register]))
        aa_i2c_write(self.aardvark, address, AA_I2C_NO_FLAGS, array("B", [data]))

    def read_register(self, address, register, word=False):
        """Read from an I2C device's register."""
        aa_i2c_write(self.aardvark, address, AA_I2C_NO_STOP, array("B", [register]))

        num_bytes = 2 if word else 1

        (count, data_in) = aa_i2c_read(self.aardvark, address, AA_I2C_NO_FLAGS, num_bytes)
        if count < 0:
            self.log.error("error: %s" % aa_status_string(count))
            return
        elif count == 0:
            self.log.error("error: no bytes read")
            self.log.error("  are you sure you have the right slave address?")
            return
        elif count != num_bytes:
            self.log.error("error: read %d bytes (expected %d)" % (count, num_bytes))
        return data_in

    def write(self, address: int, data: List):
        """Write the list of data to an address."""
        count = aa_i2c_write(self.aardvark, address, AA_I2C_NO_FLAGS, array("B", data))
        # ? Do we need to bit shift?  address

        if count < 0:
            self.log.error("error: %s" % aa_status_string(count))
        elif count == 0:
            self.log.error("error: no bytes written")
            self.log.error("  are you sure you have the right slave address?")
        elif count != len(data):
            self.log.error("error: only a partial number of bytes written")
            self.log.error("  (%d) instead of full (%d)" % (count, len(data)))

    def read(self, address: int, number_of_bytes: int):
        """Read the number of bytes from an address."""
        (count, data_in) = aa_i2c_read(self.aardvark, address, AA_I2C_NO_FLAGS, number_of_bytes)
        if count < 0:
            self.log.error("error: %s" % aa_status_string(count))
            return
        elif count == 0:
            self.log.error("error: no bytes read")
            self.log.error("  are you sure you have the right slave address?")
            return
        elif count != number_of_bytes:
            self.log.error("error: read %d bytes (expected %d)" % (count, number_of_bytes))
        return data_in
