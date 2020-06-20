import pytest


def test_basic_init(bp_loop):
    """Verify that we can connect to a bus pirate."""
    assert bp_loop.is_alive()


def test_command_and_read_byte(bp_loop):
    """Write \x01 and see if the same value is returned.

    If not it will raise CommandError.
    """
    bp_loop.command(b"\x01")
