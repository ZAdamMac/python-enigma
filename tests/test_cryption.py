import sys
from collections import Counter
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

    def test_hello_noop(self) -> None:
        plaintext = "helloworld".upper()
        expected_ctext = "ILJDQQMTQZ"
        word_length = 5
        expected_ptext = "HELLOWORLD"

        rotors = [("I", "A"), ("II", "B"), ("III", "C")]
        machine = enigma.Enigma(
            catalog="default",
            stecker="AQ BJ",
            rotors=rotors,
            reflector="Reflector B",
            operator=False,
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

        ptext = 'A' * 20

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
    """Attempt to test that the mutable defaults don't cause problems."""

    def test_default_rotor(self):
        machine1 = enigma.Enigma(catalog="default", stecker="DEF")
        machine1.set_wheels("XYZ")

        machine2 = enigma.Enigma(catalog="default", stecker="DEF")
        machine2.set_wheels("XYZ")
        machine2.set_stecker("DEF")

        ptext = "AAAAAAAAAAAAAAAA"

        ctext1 = machine1.parse(ptext)
        ctext2 = machine2.parse(ptext)

        assert ctext1 == ctext2


if __name__ == "__main__":
    sys.exit(pytest.main(args=[__file__]))
