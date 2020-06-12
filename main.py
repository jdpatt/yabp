# This file is just used to test out the library.

import logging
import time

import yabp

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger()
    bp = yabp.BusPirate()
    bp.set_mode(yabp.MODES.I2C)
    bp.i2c.start()
    bp.i2c.stop()
    bp.i2c.ack()
    bp.exit_mode()
    bp.i2c.start()
    bp.i2c.power(True)
    bp.i2c.pullups(True)
    time.sleep(1)
    bp.i2c.power(False)
    bp.i2c.pullups(False)
    bp.i2c.set_speed(3)
