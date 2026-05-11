"""Project-specific exceptions."""


class KitError(Exception):
    """Base class for expected command errors."""


class GitError(KitError):
    """Raised when git metadata cannot be read."""


class InputError(KitError):
    """Raised when user-supplied input is invalid."""
