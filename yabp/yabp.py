"""Yet Another Bus Pirate Libray"""
import logging

import serial

log = logging.getLogger("Bus Pirate")


class CommandException(Exception):
    pass


class BusPirate:
    def __init__(self, port: str, baud_rate: int = 115200, timeout: float = 0.1):
        # Configuration
        self.port = port
        self.baud_rate = baud_rate
        self.timeout = timeout

        self._serial: serial.Serial = self.connect()
        self.reset()

    def __enter__(self) -> None:
        """Allows using the bus pirate as a context manager.

        Example:

        ```python
        with BusPirate("COM3") as bp:
            bp.current_mode()
        ```

        """
        return self

    def __exit__(self, *args):
        """Clean up from using the bus pirate as a context manager."""
        self._serial.close()

    def connect(self) -> None:
        """Open the serial port."""
        try:
            ser = serial.Serial(port=self.port, baudrate=self.baud_rate, timeout=self.timeout)
            log.info(f"Connected to Bus Pirate on {self.port}")
            return ser
        except serial.serialutil.SerialException:
            log.error("Failed to connect to Bus Pirate.")
            raise

    def reset(self) -> None:
        """Reset and enter the scripting "bit bang" mode.

        Send 0x00 to the user terminal (max.) 20 times to enter the raw binary bitbang mode.
        The bp will response with BBIO1 when it succeedes.
        """
        for _ in range(0, 20):
            self._serial.write(bytes([0x00]))
            status = self._serial.read(5)
            if b"BBIO" in status:
                log.info(f"Mode: {status.decode()}")
                self._serial.reset_input_buffer()
                return
        raise CommandException("Failed to Reset Bus Pirate.")

    def exit(self) -> None:
        """Reset the Bus Pirate to the normal terminal interface.

        Send 0x0F to exit raw bitbang mode and reset the Bus Pirate.  The bp will response 0x01 on
        success.
        """
        self._serial.write(bytes([0x0F]))
        if self.is_success(self._serial.read(1)):
            log.info("Exited Scripting Mode.")

    def is_success(self, status):
        """Whenever the bus pirate succesfully completes a command, it returns b"\x01"."""
        if status == b"\x01":
            return True


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger()
    # bp = BusPirate("/dev/tty.usbserial-A901LM8T")
    # bp.exit()

    with BusPirate("/dev/tty.usbserial-A901LM8T") as bp:
        bp.exit()
