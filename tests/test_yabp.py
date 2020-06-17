import pytest
import yabp


@pytest.fixture
def bus_pirate(scope="module"):
    """Bus Pirate Fixture to share COM port across tests."""
    try:
        bp = yabp.BusPirate()
    except ConnectionError:
        pytest.skip("Test requires active bus pirate connection.")
    return bp


def test_basic_init(bus_pirate):
    """Verify that we can connect to a bus pirate."""
    assert bus_pirate.is_alive()
