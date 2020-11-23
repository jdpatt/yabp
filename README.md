# yabp

Yet Another Bus Pirate Library

Latest Version: *0.2.0*

![yabp](https://github.com/jdpatt/yabp/workflows/yabp/badge.svg)

A [Bus Pirate](http://dangerousprototypes.com/docs/Bus_Pirate) is a handy little debug tool.  Its
firmware, command documentation and artwork are released into the public domain.  The python libraries that I could find have gone untouched for many years. This is another library built from the command documentation.

This library only exposes one class `BusPirate` and an enum `MODES`.  `BusPirate` can be used for all modes and will automatically change modes as needed.  You can also explicity set the mode with `bp.set_mode(MODES.MODE_I_WANT_TO_USE)`.

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
        bp = yabp.I2C("COM3", 115200)
        bp.write_register(0x23, 0x01, 0xFF)
        bp.close()
    except ConnectionError as error:
        logging.error(error)
        raise

    # As a context manager:
    with yabp.I2C() as bp:
        bp.write_register(0x23, 0x01, 0xFF)
```
