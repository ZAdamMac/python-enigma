import sys
from collections import Counter
from collections.abc import Mapping, Sequence
from typing import Any
import pytest

from python_enigma import enigma


class TestEncrypt:
    def test_hello(self) -> None:
        plaintext = "hello world"
        expected_ctext = "ILJDQ QMTQZ"
        word_length = 5
        expected_ptext = "HELLO WORLD"

        rotors = [("I", "A"), ("II", "B"), ("III", "C")]
        machine = enigma.Enigma(
            catalog="default",
            stecker="AQ BJ",
            rotors=rotors,
            reflector="Reflector B",
            operator=True,
            word_length=word_length,
            stator="military",
        )

        machine.set_wheels("ABC")
        ctext = machine.parse(plaintext)
        assert ctext == expected_ctext

        machine.set_wheels("ABC")
        decrypted = machine.parse(ctext)
        assert decrypted == expected_ptext


class TestHistorical:
    """Tests taken from https://gist.github.com/Jither/d8dbc4d38998c18686bb646b49b9a8a6"""

    # @pytest.mark.skip("I can't get this working")
    def test_p1030681(self) -> None:
        wheels: list[str] = ["Beta", "V", "VI", "VIII"]
        rotor_positions = "CDSZ"
        ring_settings = "EPEL"
        reflector = "Reflector C Thin"
        plug_board = "AE BF CM DQ HU JN LX PR SZ VW"
        rotors = list(zip(wheels, list(rotor_positions)))

        ctext = "LANOTCTOUARBBFPMHPHGCZXTDYGAHGUFXGEWKBLKGJWLQXXTGPJJAVTOCKZFSLPPQIHZFXOEBWIIEKFZLCLOAQJULJOYHSSMBBGWHZANVOIIPYRBRTDJQDJJOQKCXWDNBBTYVXLYTAPGVEATXSONPNYNQFUDBBHHVWEPYEYDOHNLXKZDNWRHDUWUJUMWWVIIWZXIVIUQDRHYMNCYEFUAPNHOTKHKGDNPSAKNUAGHJZSMJBMHVTREQEDGXHLZWIFUSKDQVELNMIMITHBHDBWVHDFYHJOQIHORTDJDBWXEMEAYXGYQXOHFDMYUXXNOJAZRSGHPLWMLRECWWUTLRTTVLBHYOORGLGOWUXNXHMHYFAACQEKTHSJW"

        ptext = "KRKRALLEXXFOLGENDESISTSOFORTBEKANNTZUGEBENXXICHHABEFOLGELNBEBEFEHLERHALTENXXJANSTERLEDESBISHERIGXNREICHSMARSCHALLSJGOERINGJSETZTDERFUEHRERSIEYHVRRGRZSSADMIRALYALSSEINENNACHFOLGEREINXSCHRIFTLSCHEVOLLMACHTUNTERWEGSXABSOFORTSOLLENSIESAEMTLICHEMASSNAHMENVERFUEGENYDIESICHAUSDERGEGENWAERTIGENLAGEERGEBENXGEZXREICHSLEITEIKKTULPEKKJBORMANNJXXOBXDXMMMDURNHFKSTXKOMXADMXUUUBOOIEXKP"

        ptext = enigma.Operator(5).format(ptext)

        machine = enigma.Enigma(
            catalog="default",
            stecker=plug_board,
            stator="military",
            rotors=rotors,
            reflector=reflector,
            operator=True,
        )
        machine.set_wheels(ring_settings)

        decrypted = machine.parse(ctext)
        assert decrypted == ptext

    def test_greek_advance(self) -> None:
        wheels: list[str] = ["Beta", "V", "VI", "VIII"]
        rotor_positions = "CDSZ"
        ring_settings = "EPEL"
        reflector = "Reflector C Thin"
        plug_board = "AE BF CM DQ HU JN LX PR SZ VW"
        rotors = list(zip(wheels, list(rotor_positions)))

        ptext = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"

        machine = enigma.Enigma(
            catalog="default",
            stecker=plug_board,
            stator="military",
            rotors=rotors,
            reflector=reflector,
            operator=False,
        )
        machine.set_wheels(ring_settings)

        (p_most_common, p_most_commen_count) = Counter(ptext).most_common(1)[0]

        # just checking the counter logic
        assert p_most_common == "A"
        assert p_most_commen_count == len(ptext)

        ctext = machine.parse(ptext)
        (_, c_most_commen_count) = Counter(ctext).most_common(1)[0]

        # This test will fail if rotors aren't advancing
        assert c_most_commen_count != len(ctext)

        # Now we reset wheels and do the same thing again
        machine.set_wheels(ring_settings)
        ctext2 = machine.parse(ptext)

        assert ctext2 == ctext


class TestOperatorIssue:
    def testWeirdBug(self) -> None:
        """Testing for bug I cannot reproduce"""

        # copying as closely as I can from case where issue shows up
        stator = "military"
        reflector = "Reflector C Thin"

        greek_wheel = "Beta"
        wheels = [greek_wheel, "V", "VII", "VIII"]
        ring_settings = "EPEL"
        plug_board = "AE BF CM DQ HU JN LX PR SZ VW"
        rotor_position = "CDSZ"

        rotors = list(zip(wheels, list(rotor_position)))

        machine = enigma.Enigma(
            catalog="default",
            rotors=rotors,
            stecker=plug_board,
            reflector=reflector,
            operator=False,
            word_length=5,
            stator=stator,
        )
        machine.set_wheels(ring_settings)

        ptext = "A" * 20

        operator = enigma.Operator(word_length=5)

        ptext = operator.format(ptext)

        ctext = machine.parse(ptext)

        # This test will fail if rotors aren't advancing
        assert ctext[0] != ctext[1]

        # Now we reset wheels and do the same thing again
        machine.set_wheels(ring_settings)
        ctext2 = machine.parse(ptext)

        assert ctext2 == ctext


class TestDefault:
    """Test that defaults work."""

    WORKING_ARGS: Mapping[str, str | Sequence | bool | int] = {
        "catalog": "default",
        "stator": "military",
        "stecker": "AQ BJ",
        "rotors": [("I", "A"), ("II", "B"), ("III", "C")],
        "reflector": "Reflector B",
        "operator": True,
        "word_length": 5,
        "ignore_static_wheels": False,
    }
    """
    Immutable dict of argument combinations that work and should be
    compatible with defaults.
    """

    WHEEL_SETTINGS = "ABC"
    PTEXT = "HELLOWORLD"

    def default_test(self, key: str | None = None) -> None:
        kwargs: dict[str, Any] = {
            k: self.WORKING_ARGS[k] for k in self.WORKING_ARGS.keys()
        }
        if key:
            del kwargs[key]

        machine = enigma.Enigma(**kwargs)
        machine.set_wheels(self.WHEEL_SETTINGS)

        ctext = machine.parse(self.PTEXT)
        ctext = ctext.replace(" ", "")

        machine.set_wheels(self.WHEEL_SETTINGS)
        ptext = machine.parse(ctext)
        ptext = ptext.replace(" ", "")

        assert ptext == self.PTEXT

    def test_test(self) -> None:
        """Confirm that WORKING_ARGS work."""
        self.default_test()

    def test_rotor(self) -> None:
        self.default_test("rotors")

    def test_catalog(self) -> None:
        self.default_test("catalog")

    def test_stecker(self) -> None:
        self.default_test("stecker")

    def test_stator(self) -> None:
        self.default_test("stator")

    def test_reflector(self) -> None:
        self.default_test("reflector")

    def test_operator(self) -> None:
        self.default_test("operator")

    def test_word_length(self) -> None:
        self.default_test("word_length")

    def test_ignore_static_wheels(self) -> None:
        self.default_test("ignore_static_wheels")


class TestMutation:
    def test_rotor_mutation(self) -> None:
        """Fails if reference passed as rotors argument gets mutated"""
        plaintext = "hello world"

        wheels = [("I", "A"), ("II", "B"), ("III", "C")]
        wheels_copy = wheels.copy()

        machine = enigma.Enigma(
            catalog="default",
            stecker="AQ BJ",
            rotors=wheels,
            reflector="Reflector B",
            stator="military",
        )

        machine.set_wheels("ABC")
        _ = machine.parse(plaintext)
        assert wheels == wheels_copy

    def test_machine_mutation(self) -> None:
        """Fails if external change in rotors changes machine behavior."""
        plaintext = "hello world"

        wheels = [("I", "A"), ("II", "B"), ("III", "C")]

        machine = enigma.Enigma(
            catalog="default",
            stecker="AQ BJ",
            rotors=wheels,
            reflector="Reflector B",
            stator="military",
        )

        machine.set_wheels("ABC")
        ctext1 = machine.parse(plaintext)

        # Now we change wheels here
        wheels = [("IV", "A"), ("V", "B"), ("VI", "C")]
        machine.set_wheels("ABC")
        ctext2 = machine.parse(plaintext)

        assert ctext1 == ctext2


if __name__ == "__main__":
    sys.exit(pytest.main(args=[__file__]))
