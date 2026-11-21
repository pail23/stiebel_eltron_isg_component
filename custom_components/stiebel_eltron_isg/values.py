"""Shared checks for values read from the controller."""

from math import isfinite
from typing import TypeGuard


def is_finite_number(value: object) -> TypeGuard[int | float]:
    """Return True for a finite int or float that is not a bool.

    ``bool`` subclasses ``int``, and ``nan`` and ``inf`` are floats, so a plain
    ``isinstance`` check would let all three through as values.
    """
    return (
        not isinstance(value, bool)
        and isinstance(value, (int, float))
        and isfinite(value)
    )
