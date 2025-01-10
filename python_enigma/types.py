"""This is where we put types and type-like classes"""

from typing import NewType, TypedDict


class RotorSpec(TypedDict):
    """The fixed details defining a rotor"""

    name: str
    wiring: dict[str, int]
    notch: str
    static: bool


Char = NewType("Char", str)
"""Intended to indicate single ASCII character.

Note that the the intention is not enforced.
"""
