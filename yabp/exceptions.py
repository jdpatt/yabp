"""Exceptions for yabp."""


class CommandError(Exception):
    """A command failed to either execute or return a response."""


class DeviceError(Exception):
    """The device failed to response correctly."""
