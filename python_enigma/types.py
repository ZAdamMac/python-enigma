"""This is where we put types and type-like classes"""

from typing import TypedDict


class RotorSpec(TypedDict):
    """The fixed details defining a rotor"""

    name: str
    wiring: dict[str, int]
    notch: str
    static: bool


class Char(str):
    """Intended to indicate single ASCII character.

    This also implements type preserving ``upper`` and ``lower``,
    but think of this as a type instead of a full-blown class.
    """

    def upper(self) -> "Char":
        return Char(super().upper())

    def lower(self) -> "Char":
        return Char(super().lower())
