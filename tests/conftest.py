from unittest.mock import patch

import pytest
import serial

import yabp


@pytest.fixture(scope="function")
@patch.object(
    yabp.Base, "open", return_value=serial.serial_for_url("loop://?logging=debug", timeout=1)
)
def bp_loop(mock_serial_port):
    """Loop Back Serial port for tests that don't require a bus pirate."""
    return yabp.Base()


@pytest.fixture(scope="module")
def bus_pirate():
    """Bus Pirate Fixture to share COM port across tests."""
    try:
        bp = yabp.Base()
    except ConnectionError:
        pytest.skip("Test requires active bus pirate connection.")
    return bp
