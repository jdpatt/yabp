# This file is just used to test out the library.

import logging
import time

import yabp

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger()
    logging.getLogger("yabp").setLevel(logging.ERROR)

    try:
        bp = yabp.BusPirate()
        bp.i2c.write_register(0x23, 0x01, 0xFF)
        bp.close()
    except ConnectionError as error:
        logging.error(error)
        raise

    with yabp.BusPirate() as bp:
        bp.i2c.write_register(0x23, 0x01, 0xFF)
