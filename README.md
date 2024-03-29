# yabp

Yet Another Bus Pirate Library

Latest Version: *1.1.0*

![yabp](https://github.com/jdpatt/yabp/workflows/yabp/badge.svg)

A [Bus Pirate](http://dangerousprototypes.com/docs/Bus_Pirate) is a handy little debug tool.  Its
firmware, command documentation and artwork are released into the public domain.  The python libraries that I could find have gone untouched for many years. This is another library built from the command documentation.

## Developer Install

1. `git clone https://github.com/jdpatt/yabp.git`
2. `cd yabp`
3. Create a virtual environment with `python -m venv .venv`
4. Activate that environment
5. `pip install -r requirements-dev.txt`
6. `pre-commit install`
7. `pip install -e .`
8. `tox`

## Usage

```python

import logging
import time

import yabp

if __name__ == "__main__":
    # Create a generic root logger.
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger()

    # Change the message level of yabp.
    logging.getLogger("yabp").setLevel(logging.ERROR)

    # Traditional usage:
    try:
        bp = yabp.I2C("COM3", 115200)  # Specified the com port and baud rate.
        bp.write_register(address=0x23, register=0x01, data=0xFF)
        bp.close()
    except ConnectionError as error:
        logging.error(error)
        raise

    # Or as a context manager:
    with yabp.I2C() as bp:  # Let the library find the correct serial port.
        bp.write_register(0x23, 0x01, 0xFF)
```
