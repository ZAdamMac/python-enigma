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
import json

class SteckerSettingsInvalid(Exception):
    """Raised if the stecker doesn't like its settings - either a duplicated
    letter was used or a non-letter character was used.
    """

class UndefinedStatorError(Exception):
    """Raised if the stator mode string is not a defined stator type
    """

class RotorNotFound(Exception):
    """Raised if the rotor requested is not found in the catalogue
    """


class Stecker(object):
    """A class implementation of the stecker. The stecker board was a set of
    junctions which could rewire both the lamps and keys for letters in a
    pairwise fashion. This formed a sort of double-substitution step. The
    stecker board eliminated an entire class of attacks against the machine.

    This stecker provides a method "steck" which performs the substitution.
    """

    def __init__(self, setting):
        """Accepts a string of space-seperated letter pairs denoting stecker
         settings, deduplicates them and grants the object its properties.
        """
        stecker_pairs = setting.upper().split(" ")
        used_characters = []
        valid_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        self.stecker_setting = {}
        for pair in stecker_pairs:
            if (pair[0] in used_characters) or (pair[1] in used_characters):
                raise SteckerSettingsInvalid
            elif (pair[0] not in valid_chars) or (pair[1] not in valid_chars):
                raise SteckerSettingsInvalid
            else:
                self.stecker_setting.update({pair[0]: pair[1]})
                self.stecker_setting.update({pair[1]: pair[0]})

    def steck(self, char):
        """Accepts a character and parses it through the stecker board.
        """
        if char.upper() in self.stecker_setting:
            return self.stecker_setting[char]
        else:
            return char  # Un-jumped characters should be returned as is.


class Stator(object):
    """The stator was the first "wheel" of the enigma, which was stationary
    and usually never changed. However, as different machines used different
    variations of the stator, we do have to represent it even if its is
    not stateful. Two stators are provided for - these are the historical
    versions. Use "stat" to actually perform the stator's function, and
    "destat" to do the same in reverse.
    """

    def __init__(self, mode):
        """The stator mode is a string which states which stator to use. As
        currently implemented the options are "civilian" or "military"
        """
        mode = mode.lower()
        if mode == "civilian":
            self.stator_settings = {
                "Q": 1, "W": 2, "E": 3, "R": 4, "T": 5, "Z": 6, "U": 7, "I": 8,
                "O": 9, "P": 10, "A": 11, "S": 12, "D": 13, "F": 14, "G": 15,
                "H": 16, "J": 17, "K": 18, "L": 19, "Y": 20, "X": 21, "C": 22,
                "V": 23, "B": 24, "N": 25, "M": 26,
            }
        elif mode == "military":
            self.stator_settings = {
                "A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6, "G": 7, "H": 8,
                "I": 9, "J": 10, "K": 11, "L": 12, "M": 13, "N": 14, "O": 15,
                "P": 16, "Q": 17, "R": 18, "S": 19, "T": 20, "U": 21, "V": 22,
                "W": 23, "X": 24, "Y": 25, "Z": 26,
            }
        else:
            raise UndefinedStatorError

        self.destator = {}
        for key in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            reflected = self.stator_settings[key]
            self.destator.update({reflected: key})

    def stat(self, char):
        char = char.upper()
        return self.stator_settings[char]

    def destat(self, signal):
        return self.destator[signal]


class Rotor(object):
    """This simple class represents a single rotor object. The rotors themselves
    are defined in RotorSettings.json of this package. Select a rotor by provding
    the rotor-type and Ringstellung while initializing.

    It's worth noting the reflector is also treated as a rotor.
    """
    def __init__(self, catalog, rotor_number, ringstellung):
        """Initialize the parameters of this individual rotor.

        :param catalog: A dictionary describing all rotors available.
        :param rotor_number: A rotor descriptor which can be found as a key in catalog
        :param ringstellung: The desired offset letter as a string.
        """
        if rotor_number in catalog:
            description = catalog[rotor_number]
        else:
            raise RotorNotFound
        if ringstellung is None:
            ringstellung = 0
        ringstellung = alpha_to_index(ringstellung.upper())

        self.notch = []
        for position in description["notch"]:
            self.notch.append(alpha_to_index(position))
        self.wiring = {}
        self.wiring_back = {}
        for key in description["wiring"]:
            trace = description["wiring"][key]
            new_in = int(key)  # Also known as "default_in"
            new_out = int(trace)
            new_in += ringstellung
            new_out += ringstellung
            if new_in > 26:  # Lazy Man's Modular Addition
                new_in -= 26
            if new_out > 26:
                new_out -= 26
            self.wiring.update({new_in: new_out})
            self.wiring_back.update({new_out: new_in})


class RotorMechanism(object):
    """This class represents and emulates the entire "moving parts" state of
    the machine. Essentially, this keeps track of the rotors and their
    positions. You can process characters one at a time through this object's
    "process" method. Initial settings are passed with the "set" method.
    """
    def __init__(self, list_rotors, reflector):
        """Expects a list of rotors and a rotor object representing reflector"""
        self.rotors = list_rotors
        for rotor in self.rotors:
            rotor.position = 1
        self.reflector = reflector

    def set(self, rotor_slot, setting):
        """Expects a python-indexed rotor and a character for a setting"""
        self.rotors[rotor_slot].position = alpha_to_index(setting)

    def process(self, bit_in):
        """Expects the pinning code from Stator, and returns an output
        of a similar nature. Also increments the state by adjusting the
        position attribute of each rotor in its set. On each operation
        the position bit is added at both ends."""
        next_bit = bit_in
        for rotor in self.rotors:
            transit_a = next_bit
            transit_b = addMod26(transit_a, rotor.position)
            next_bit = addMod26(rotor.wiring[transit_b], rotor.position)
        next_bit = self.reflector.wiring[next_bit]
        for rotor in reversed(self.rotors):
            transit_a = next_bit
            transit_b = subMod26(transit_a, rotor.position)
            next_bit = subMod26(rotor.wiring_back[transit_b], rotor.position)

        output = next_bit

        indexing = 0
        step_next = False
        first = True  # Lazy hack to catch the first time we step through.
        for rotor in self.rotors:
            rotor.step_me = False
            if first or step_next:  # First rotor ALWAYS steps.
                rotor.step_me = True
            first = False
            step_next = False
            if rotor.position == rotor.notch:
                step_next = True
            if step_next:
                if self.rotors[indexing+1].position == self.rotors[indexing+1].notch:
                    self.rotors[indexing+2].step_me = True
            indexing += 1

        for rotor in self.rotors:
            if rotor.step_me:
                rotor.position += 1
                if rotor.position > 26:
                    rotor.position -= 26

        for rotor in self.rotors:
            rotor.step_me = False

        return output


class Operator(object):
    """A special preparser that does some preformatting to the feed. This
    includes adjusting the spacing and stripping out characters that can't
    be represented easily in Enigma. This operator is not faithful to
    German practice at the time - it's only a convenience.
    """

    def __init__(self, word_length):
        """word_length is an int that sets the length of "words" in output."""
        self.word_length = word_length

    def format(self, message):
        """Accepts a string as input and does some parsing to it."""
        cased_message = message.upper()
        message_characters = cased_message.replace(" ", "")
        dict_replacement_characters = {".": "X", ":": "XX", ",": "ZZ", "?": "FRAQ",
                                       "(": "KLAM", ")": "KLAM", """'""": "X"}
        for punct in dict_replacement_characters:
            message_characters = message_characters.replace(punct, dict_replacement_characters[punct])

        for character in message_characters:
            if character not in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                message_characters = message_characters.replace(character, "")

        m = message_characters
        # This next step adds the spaces which cut the words up.
        message_spaced = ' '.join([m[i:i+self.word_length] for i in range(0, len(message_characters), self.word_length)])
        return message_spaced


class Enigma(object):
    """A magic package that instantiates everything, allowing you to call your
    enigma machine as though it were a machine and operator pair. Allows these
    methods:
    - parse: processes a str message, outputing raw characters. Spacing is
    preserved if operator=False, otherwise it will be changed to word_length.
    If no operator is present, numerals and punctuation are unchanged.
    - set: change various settings. See below.
    """

    def __init__(self, catalog={}, stecker="", stator="military",
                 rotors=[["I",0], ["II",0], ["III",0]],
                 reflector="UKW", operator=True, word_length=5,):
        self.stecker = Stecker(setting=str(stecker))
        self.stator = Stator(mode=stator)
        # We have to reverse the rotors as we insert them because the signal
        # originates at the right-hand edge of the wheelpack.
        if catalog == "default":
            with open("catalogue.json", "r") as file:
                catalog = json.load(file)
        wheels = []
        rotors.reverse()
        for rotor in rotors:
            rotor_req = rotor[0]
            ringstellung = rotor[1]
            rotor_object = Rotor(catalog, rotor_req, ringstellung)
            wheels.append(rotor_object)
        self.wheel_pack = RotorMechanism(wheels, reflector=Rotor(catalog,rotor_number=reflector, ringstellung="A"))
        if operator:
            if isinstance(operator, Operator):
                self.operator = operator(word_length)
            else:
                self.operator = Operator(word_length)
        else:
            self.operator = False

    def set_wheels(self, setting):
        """Accepts a string that is the new pack setting, e.g. ABQ"""
        physical_setting = []
        for char in setting:
            physical_setting.append(char.upper())
        physical_setting.reverse()
        for i in range(0, len(physical_setting)):
            self.wheel_pack.set(i, physical_setting[i])

    def set_stecker(self, setting):
        """Accepts a string to be the new stecker board arrangement."""
        self.stecker = Stecker(setting=str(setting))

    #def set_wheelpack(self, list_rotors):
        #self.wheel_pack = RotorMechanism(list_rotors.reverse())

    def parse(self, message="Hello World"):
        if self.operator:
            str_message = self.operator.format(message)
        else:
            str_message = message.upper()

        str_ciphertext = ""
        for character in str_message:
            if character in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                stecked = self.stecker.steck(character)  # Keystroke - > Stecker
                stated = self.stator.stat(stecked)  # Stecker -> Stator Wheel
                polysubbed = self.wheel_pack.process(stated)  # Both ways through wheelpack, wheelpack steps forward.
                destated = self.stator.destat(polysubbed)  # Backward through the stator wheel
                lamp = self.stecker.steck(destated)  # Again through stecker
                next_char = lamp
            else: # Raised if an unformatted message contains special characters
                next_char = character
            str_ciphertext += next_char

        return str_ciphertext


def alpha_to_index(char):
    """Takes a single character and converts it to a number where A=0"""
    translator = {
                "A": 0, "B": 1, "C": 2, "D": 3, "E": 4, "F": 5, "G": 6, "H": 7,
                "I": 8, "J": 9, "K": 10, "L": 11, "M": 12, "N": 13, "O": 14,
                "P": 15, "Q": 16, "R": 17, "S": 18, "T": 19, "U": 20, "V": 21,
                "W": 22, "X": 23, "Y": 24, "Z": 25,
            }
    return translator[char.upper()]


def alpha_to_num(char):
    """Takes a single character and converts it to a number where A=1"""
    translator = {
                "A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6, "G": 7, "H": 8,
                "I": 9, "J": 10, "K": 11, "L": 12, "M": 13, "N": 14, "O": 15,
                "P": 16, "Q": 17, "R": 18, "S": 19, "T": 20, "U": 21, "V": 22,
                "W": 23, "X": 24, "Y": 25, "Z": 26,
            }
    return translator[char.upper()]


def addMod26(original, add):
    undiff = original + add
    if undiff > 26:
        undiff -= 26
    return undiff


def subMod26(original, less):
    diff = original - less
    if diff < 1:
        diff += 26
    return diff