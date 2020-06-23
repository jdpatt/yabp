from contextlib import nullcontext as does_not_raise

import pytest
from yabp.exceptions import CommandError


def test_basic_init(bp_loop):
    """Verify that we can connect to a bus pirate."""
    assert bp_loop.is_alive()


@pytest.mark.parametrize(
    "tests, expected", [(b"\x01", does_not_raise()), (b"\x00", pytest.raises(CommandError))]
)
def test_command_and_read_byte(bp_loop, tests, expected):
    """Write \x01 and see if the same value is returned. If not, raise CommandError."""
    with expected:
        bp_loop.command(tests)
