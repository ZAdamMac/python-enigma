import sys
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

        machine = enigma.Enigma(
            catalog="default",
            stecker=plug_board,
            stator="military",
            rotors=rotors,
            reflector=reflector,
            operator=False,
        )
        machine.set_wheels(ring_settings)

        decrypted = machine.parse(ctext)
        assert decrypted == ptext


if __name__ == "__main__":
    sys.exit(pytest.main(args=[__file__]))
