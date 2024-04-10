"""Validating functions."""

import variables


def has_flag(flag: str, path: str) -> bool:
    """Check if an ignore flag applies in the path's context."""
    flags = set()
    for key, value in variables.FLAGS.items():
        if path.startswith(key):
            flags.update(value)

    return flag in flags
