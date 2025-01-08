import csv
import json
import os
from python_enigma import enigma

catalogue = {}

with open("table_rotors.csv", "r") as file:
    reading = csv.reader(file)
    for line in reading:
        rotor_label = line[0]
        bindings_dict = {}
        counter = 1
        for character in line[1]:
            binding = enigma.alpha_to_num(character.upper())
            new_entry = {counter: binding}
            bindings_dict.update(new_entry)
            counter += 1
        notch = line[2]

        catalogue.update({rotor_label: {"wiring": bindings_dict, "notch": notch}})

with open("catalogue.json", "w") as out:
    json.dump(catalogue, out)
print("Done")
exit()
