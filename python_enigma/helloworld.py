"""This is a simple example hello-world script for using this engima module."""

from python_enigma import enigma
import json

with open("catalogue.json", "r") as file:
    all_wheels = json.load(file)

use_these = [("I", "A"), ("II", "B"), ("III", "C")]
machine = enigma.Enigma(catalog="default", stecker="QZ",
                        rotors=use_these, reflector="Reflector B", operator=True, word_length=5, stator="military")
machine.set_wheels("ABC")

print("I am going to try to print HELLO WORLD using the stecker settings\n"
      "AQ and BJ and rotors I, II, III from the whermact set.\n"
      "The ringstellungs are A, B, and C respectively.")
crypted = machine.parse("hello world")
print(crypted)
print("If I feed that back through, it decrypts to:")
machine.set_wheels("ABC")
print(machine.parse(crypted))
exit()