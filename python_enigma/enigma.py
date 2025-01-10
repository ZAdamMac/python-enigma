"""An implementation of the Enigma Machine in Python.

This is a toy project intending to implement the Enigma Machine as originally
designed by Arthur Scherbius. Enigma was an electromechanical implementation of
a polyalphabetic substitution cypher. It's no longer considered
cryptographically secure, but the device itself was fairly interesting.

No effort has been made to correct any of the cryptographic flaws in enigma;
this implementation is meant to be as faithful as possible. Additionally,
steps have been taken to attempt to emulate not just the Wehrmacht enigma, but
the commercial models as well. Additionally while a large number of rotor
bindings can be found in the provided catalog.json, this is not exhaustive,
and the module makes no effort to enforce the use of "matching" rotors.

No interactive mode is explicitly provided for - import into an interactive
interpreter or call with your scriptlets.

Development was by Zac Adam-MacEwen. See the README.md for details.

"""

# General Purpose Imports Block
from collections import UserDict
import json
from typing import Any, Optional
from collections.abc import Mapping, Sequence
import importlib.resources as ir
import python_enigma.resources
from python_enigma.types import Char, RotorSpec


class SteckerSettingsInvalid(Exception):
    """Raised if the stecker doesn't like its settings - either a duplicated
    letter was used or a non-letter character was used.
    """


class UndefinedStatorError(Exception):
    """Raised if the stator mode string is not a defined stator type"""


class RotorNotFound(Exception):
    """Raised if the rotor requested is not found in the catalogue"""


class ReflectorNotFound(Exception):
    """Raised if the reflector requested is not found in the catalogue"""


class Catalog(UserDict[str, RotorSpec]):
    """
    This class will eventually be a dict of rotors,
    but the Rotor class needs to be modified before that happens.
    So in the current version this just has the load default method.
    """

    CATALOG_FILE_NAME = "catalogue.json"
    CATALOG_FILE_DIR = ir.files(python_enigma.resources)
    CATALOG_FILE_PATH = CATALOG_FILE_DIR.joinpath(CATALOG_FILE_NAME)

    default_data: Optional[Mapping[str, Any]] = None

    @classmethod
    def default(cls) -> "Catalog":
        """Returns the default catalogue."""
        if cls.default_data is None:
            with cls.CATALOG_FILE_PATH.open("r") as f:
                cls.default_data = json.load(f)
        assert cls.default_data is not None

        for k, v in cls.default_data.items():
            v["name"] = k
            if "static" not in v:
                v["static"] = False

        return Catalog(cls.default_data)


class Stecker:
    """A class implementation of the stecker. The stecker board was a set of
    junctions which could rewire both the lamps and keys for letters in a
    pairwise fashion. This formed a sort of double-substitution step. The
    stecker board eliminated an entire class of attacks against the machine.

    This stecker provides a method "steck" which performs the substitution.
    """

    def __init__(self, setting: Optional[str]) -> None:
        """Accepts a string of space-separated letter pairs denoting stecker
        settings, deduplicates them and grants the object its properties.
        """
        self.stecker_setting: dict[Char, Char] = {}
        if setting is not None:
            stecker_pairs = setting.upper().split(" ")
            used_characters: list[Char] = []
            valid_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            for pair in stecker_pairs:
                if (pair[0] in used_characters) or (pair[1] in used_characters):
                    raise SteckerSettingsInvalid
                elif (pair[0] not in valid_chars) or (pair[1] not in valid_chars):
                    raise SteckerSettingsInvalid
                else:
                    p0 = Char(pair[0])
                    p1 = Char(pair[1])
                    self.stecker_setting[p0] = p1
                    self.stecker_setting[p1] = p0

    def steck(self, char: Char) -> Char:
        """Accepts a character and parses it through the stecker board."""
        if char.upper() in self.stecker_setting:
            return self.stecker_setting[char]
        else:
            return char  # Un-jumped characters should be returned as is.

    def __repr__(self) -> str:
        settings = []
        for fromchar, tochar in self.stecker_setting.items():
            if tochar + fromchar not in settings:
                settings.append(fromchar + tochar)
        return f'Stecker("{" ".join(settings)}")'


class Stator:
    """The stator was the first "wheel" of the enigma, which was stationary
    and usually never changed. However, as different machines used different
    variations of the stator, we do have to represent it even if its is
    not stateful. Two stators are provided for - these are the historical
    versions. Use "stat" to actually perform the stator's function, and
    "destat" to do the same in reverse.
    """

    def __init__(self, mode: str) -> None:
        """The stator mode is a string which states which stator to use. As
        currently implemented the options are "civilian" or "military"
        """
        mode = mode.lower()
        self.mode = mode
        stator_settings: dict[str, int]
        if mode == "civilian":
            stator_settings = {
                "Q": 1, "W": 2, "E": 3, "R": 4, "T": 5, "Z": 6, "U": 7,
                "I": 8, "O": 9, "P": 10, "A": 11, "S": 12, "D": 13, "F": 14, "G": 15, "H": 16, "J": 17, "K": 18, "L": 19, "Y": 20, "X": 21,
                "C": 22, "V": 23, "B": 24, "N": 25, "M": 26,
            }  # fmt: skip
        elif mode == "military":
            stator_settings = {
                "A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6,
                "G": 7, "H": 8, "I": 9, "J": 10, "K": 11, "L": 12,
                "M": 13, "N": 14, "O": 15, "P": 16, "Q": 17, "R": 18,
                "S": 19, "T": 20, "U": 21, "V": 22, "W": 23, "X": 24,
                "Y": 25, "Z": 26,
                }  # fmt: skip
        else:
            raise UndefinedStatorError

        self.stator_settings: dict[Char, int] = {
            Char(c): n for c, n in stator_settings.items()
        }

        self.destator: dict[int, Char] = {n: c for c, n in self.stator_settings.items()}

    def stat(self, char: Char) -> int:
        char = Char(char.upper())
        return self.stator_settings[char]

    def destat(self, signal: int) -> Char:
        return self.destator[signal]

    def __repr__(self) -> str:
        return f"Stator({self.mode!r})"


class Rotor:
    """This simple class represents a single rotor object. The rotors themselves
    are defined in RotorSettings.json of this package. Select a rotor by provding
    the rotor-type and Ringstellung while initializing.

    It's worth noting the reflector is also treated as a rotor.
    """

    def __init__(
        self,
        catalog: Catalog,
        rotor_number: str,
        ringstellung: str,
        ignore_static: bool,
    ):
        """Initialize the parameters of this individual rotor.

        :param catalog: A dictionary describing all rotors available.
        :param rotor_number:
            A rotor descriptor which can be found as a key in catalog
        :param ringstellung: The desired offset letter as a string.
        """
        self.name = rotor_number
        self.step_me = False
        self.static = False
        self.catalog = catalog
        self.ignore_static = ignore_static
        if rotor_number in catalog:
            description = catalog[rotor_number]
        else:
            raise RotorNotFound(rotor_number)

        self.ringstellung: int = alpha_to_num(Char("A"))
        if ringstellung is not None:
            self.ringstellung = alpha_to_num(Char(ringstellung.upper()))

        self.position: int

        # Extremely nasty ringstellung implementation follows.
        # For this to work, ringstellung needs to be a number,
        # rather than an index.

        ringstellunged_to_keys = {}  # ringstellung offset for entry pins.
        pins_to_ringstellunged = {}  # ringstellung offset for exit pins.

        pos = self.ringstellung
        for i in range(1, 27):
            if pos > 26:
                pos -= 26
            ringstellunged_to_keys[pos] = i
            pins_to_ringstellunged[i] = pos
            pos += 1

        self.notch = []
        for position in description["notch"]:
            self.notch.append(alpha_to_index(Char(position)))
        self.wiring = {}
        self.wiring_back = {}

        for shifted_input in ringstellunged_to_keys:
            in_pin = ringstellunged_to_keys[shifted_input]
            out_pin = pins_to_ringstellunged[description["wiring"][str(in_pin)]]
            self.wiring[shifted_input] = out_pin
            self.wiring_back[out_pin] = shifted_input

        if not ignore_static:
            if (
                "static" in description.keys()
            ):  # Issue 4: Bravo and Gamma rotor need to be static for m4
                if description["static"]:
                    self.static = True
                else:
                    self.static = False

    def __repr__(self) -> str:
        return f'Rotor("{self.catalog!r}", {self.name!r}", {self.ringstellung!r}, {self.ignore_static!r})'


class RotorMechanism:
    """This class represents and emulates the entire "moving parts" state of
    the machine. Essentially, this keeps track of the rotors and their
    positions. You can process characters one at a time through this object's
    "process" method. Initial settings are passed with the "set" method.
    """

    def __init__(self, list_rotors: list[Rotor], reflector: Rotor) -> None:
        """Expects list of rotors and a rotor object representing reflector"""
        self.rotors = list_rotors
        for rotor in self.rotors:
            rotor.position = 1
        self.reflector = reflector

    def set(self, rotor_slot: int, setting: Char) -> None:
        """Expects a python-indexed rotor and a character for a setting"""
        self.rotors[rotor_slot].position = alpha_to_index(setting)

    def process(self, bit_in: int) -> int:
        """Expects the pinning code from Stator, and returns an output
        of a similar nature. Also increments the state by adjusting the
        position attribute of each rotor in its set. On each operation
        the position bit is added at both ends."""

        next_bit = bit_in

        self.rotors[0].step_me = True  # The rightmost rotor always steps.
        indexer = -1
        for rotor in self.rotors:
            indexer += 1
            if (
                rotor.position in rotor.notch
            ):  # If a rotor is at its notch, the one on the left steps.
                if rotor.step_me:
                    try:
                        self.rotors[indexer + 1].step_me = True
                    except IndexError:
                        pass

        for rotor in self.rotors:
            if not rotor.static:  # Edge Case: The M4 B & C rotors don't rotate.
                if rotor.step_me:
                    rotor.step_me = False  # We gonna step now.
                    rotor.position += 1
                    if rotor.position > 25:  # Position can't exceed 25.
                        rotor.position -= 26

        for rotor in self.rotors:
            entry_face, exit_face = map_faces(rotor)
            entry_pin = entry_face[next_bit]
            exit_pin = rotor.wiring[entry_pin]
            next_bit = exit_face[exit_pin]
        next_bit = self.reflector.wiring[next_bit]
        for rotor in reversed(self.rotors):
            entry_face, exit_face = map_faces(rotor)
            entry_pin = entry_face[next_bit]
            exit_pin = rotor.wiring_back[entry_pin]
            next_bit = exit_face[exit_pin]

        output = next_bit

        return output

    def __repr__(self) -> str:
        return f"RotorMechanism({self.rotors!r}, {self.reflector!r})"


class Operator:
    """A special pre-parser that does some pre-formatting to the feed. This
    includes adjusting the spacing and stripping out characters that can't
    be represented easily in Enigma. This operator is not faithful to
    German practice at the time - it's only a convenience.
    """

    def __init__(self, word_length: int) -> None:
        """word_length is an int that sets the length of "words" in output."""
        self.word_length = word_length

    def format(self, message: str) -> str:
        """Accepts a string as input and does some parsing to it."""
        cased_message = message.upper()
        message_characters = cased_message.replace(" ", "")
        dict_replacement_characters = {
            ".": "X",
            ":": "XX",
            ",": "ZZ",
            "?": "FRAQ",
            "(": "KLAM",
            ")": "KLAM",
            """'""": "X",
        }
        for punct in dict_replacement_characters:
            message_characters = message_characters.replace(
                punct, dict_replacement_characters[punct]
            )

        for character in message_characters:
            if character not in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                message_characters = message_characters.replace(character, "")

        m = message_characters
        # This next step adds the spaces which cut the words up.
        message_spaced = " ".join(
            [
                m[i : i + self.word_length]
                for i in range(0, len(message_characters), self.word_length)
            ]
        )
        return message_spaced

    def __repr__(self) -> str:
        return f"Operator({self.word_length!r})"


class Enigma:
    """A magic package that instantiates everything, allowing you to call your
    enigma machine as though it were a machine and operator pair. Allows these
    methods:
    - parse: processes a str message, outputing raw characters. Spacing is
    preserved if operator=False, otherwise it will be changed to word_length.
    If no operator is present, numerals and punctuation are unchanged.
    - set: change various settings. See below.
    """

    def __init__(
        self,
        catalog: Catalog | str = "default",
        stecker: str | None = None,
        stator: str = "military",
        rotors: Sequence[Sequence[str]] = (("I", "A"), ("II", "A"), ("III", "A")),
        reflector: str = "UKW",
        operator: bool | Operator = True,
        word_length: int = 5,
        ignore_static_wheels: bool = False,
    ) -> None:
        self.stecker = Stecker(setting=stecker)
        self.stator = Stator(mode=stator)
        # We want to _copy_ values for rotors, as original might be mutable.
        self.rotor_names = tuple((w[0], w[1]) for w in rotors)
        self.reflector_name = reflector
        self.operator_param = operator
        self.ignore_static_wheels = ignore_static_wheels
        # We have to reverse the rotors as we insert them because the signal
        # originates at the right-hand edge of the wheelpack.

        if isinstance(catalog, str):
            if catalog != "default":
                raise ValueError('Must be a Catalog or "default".')
            catalog = Catalog.default()
        self.catalog = catalog
        wheels = []
        rotors = rotors[::-1]  # reverse the tuple
        for rotor in rotors:
            rotor_req = rotor[0]
            ringstellung = rotor[1]
            rotor_object = Rotor(
                self.catalog, rotor_req, ringstellung, ignore_static_wheels
            )
            wheels.append(rotor_object)
        try:
            reflector_rotor = Rotor(
                self.catalog,
                rotor_number=reflector,
                ringstellung="A",
                ignore_static=ignore_static_wheels,
            )
        except RotorNotFound:
            raise ReflectorNotFound(reflector) from None
        self.wheel_pack = RotorMechanism(wheels, reflector=reflector_rotor)

        # For backwards compatibility, the operator parameter has two very
        # different meanings depending on type. But we will make self.operator
        # more sensible.
        self.operator: Optional[Operator] = None

        if isinstance(operator, Operator):
            self.operator = operator
        elif operator:  # It's a bool
            self.operator = Operator(word_length)

    def set_wheels(self, setting: str) -> None:
        """Accepts a string that is the new pack setting, e.g. ABQ"""
        physical_setting: list[Char] = []
        for char in setting:
            physical_setting.append(Char(char.upper()))
        physical_setting.reverse()
        for i in range(0, len(physical_setting)):
            self.wheel_pack.set(i, physical_setting[i])

    def set_stecker(self, setting: str) -> None:
        """Accepts a string to be the new stecker board arrangement."""
        self.stecker = Stecker(setting)

    # def set_wheelpack(self, list_rotors):
    # self.wheel_pack = RotorMechanism(list_rotors.reverse())

    def parse(self, message: str = "Hello World") -> str:
        if self.operator:
            str_message = self.operator.format(message)
        else:
            str_message = message.upper()

        str_ciphertext = ""
        for character in str_message:
            character = Char(character)
            if character in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                stecked = self.stecker.steck(character)  # Keystroke - > Stecker
                stated = self.stator.stat(stecked)  # Stecker -> Stator Wheel
                polysubbed = self.wheel_pack.process(
                    stated
                )  # Both ways through wheelpack, wheelpack steps forward.
                destated = self.stator.destat(
                    polysubbed
                )  # Backward through the stator wheel
                lamp = self.stecker.steck(destated)  # Again through stecker
                next_char = lamp
            else:  # Raised if an unformatted message contains special characters
                next_char = character
            str_ciphertext += next_char

        return str_ciphertext

    def __repr__(self) -> str:
        return f"""Enigma(catalog={self.catalog},
stecker={self.stecker.__repr__()},
stator={self.stator.__repr__()},
rotors={self.rotor_names},
reflector={self.reflector_name},
operator={self.operator_param},
word_length={self.operator.word_length if self.operator else 'NA'},
ignore_static_wheels={self.ignore_static_wheels})"""


def alpha_to_index(char: Char) -> int:
    """Takes a single character and converts it to a number where A=0"""
    translator = {
        "A": 0, "B": 1, "C": 2, "D": 3, "E": 4, "F": 5,
        "G": 6, "H": 7, "I": 8, "J": 9, "K": 10,
        "L": 11, "M": 12, "N": 13, "O": 14, "P": 15,
        "Q": 16, "R": 17, "S": 18, "T": 19, "U": 20,
        "V": 21, "W": 22, "X": 23, "Y": 24, "Z": 25,
    }  # fmt: skip
    return translator[char.upper()]


def alpha_to_num(char: Char) -> int:
    """Takes a single character and converts it to a number where A=1"""
    translator = {
        "A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6,
        "G": 7, "H": 8, "I": 9, "J": 10, "K": 11, "L": 12,
        "M": 13, "N": 14, "O": 15, "P": 16, "Q": 17, "R": 18,
        "S": 19, "T": 20, "U": 21, "V": 22, "W": 23, "X": 24,
        "Y": 25, "Z": 26,
    }  # fmt: skip
    return translator[char.upper()]


def num_to_alpha(integ: int) -> str:
    """takes a numeral value and spits out the corresponding letter."""
    translator = {
        1: "A", 2: "B", 3: "C", 4: "D", 5: "E", 6: "F",
        7: "G", 8: "H", 9: "I", 10: "J", 11: "K", 12: "L",
        13: "M", 14: "N", 15: "O", 16: "P", 17: "Q", 18: "R",
        19: "S", 20: "T", 21: "U", 22: "V", 23: "W", 24: "X",
        25: "Y", 26: "Z",
    }  # fmt: skip
    return translator[integ]


def map_faces(rotor: Rotor) -> tuple[dict[int, int], dict[int, int]]:
    """Are you ready for bad entry pinning mapping?"""

    pos = rotor.position + 1  # We need a pin number, rather than an index
    neutral_to_pins: dict[int, int] = dict()
    pins_to_neutral: dict[int, int] = dict()

    for i in range(1, 27):
        if pos > 26:
            pos -= 26
        neutral_to_pins[i] = pos
        pins_to_neutral[pos] = i  # This is probably not right...
        pos += 1

    return neutral_to_pins, pins_to_neutral
