# yabp

Yet Another Bus Pirate Libray

A [Bus Pirate](http://dangerousprototypes.com/docs/Bus_Pirate) is a handy little debug tool.  Its
firmware, command documentation and artwork are released into the public domain.  This is another library built from the command documentation but fits my needs and doesn't carry the GPL notice that is tucked away in the *pyBusPirateLite* that is under the scripts folder or any similar derivatives.  They have gone untouched for many years.

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
        bp = yabp.BusPirate()
        bp.i2c.write_register(0x23, 0x01, 0xFF)
        bp.close()
    except ConnectionError as error:
        logging.error(error)
        raise

    # As a context manager:
    with yabp.BusPirate() as bp:
        bp.i2c.write_register(0x23, 0x01, 0xFF)
```
