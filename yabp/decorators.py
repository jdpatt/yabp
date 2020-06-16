"""Decorators used in yabp."""
import functools


def check_bp_mode(func):
    """Verify the bus pirate is in the correct mode."""

    @functools.wraps(func)
    def wrapper_decorator(self, *args, **kwargs):
        self.bp.set_mode(self.required_mode)
        value = func(self, *args, **kwargs)
        return value

    return wrapper_decorator


def check_mode(func):
    """Verify the bus pirate is in the base mode."""

    @functools.wraps(func)
    def wrapper_decorator(self, *args, **kwargs):
        self.exit_mode()
        value = func(self, *args, **kwargs)
        return value

    return wrapper_decorator
