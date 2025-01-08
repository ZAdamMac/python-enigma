# python-enigma: Engima Machines, But With Python

This project introduces a package, python_enigma, with an `enigma` module which can be imported and used to include Enigma-Machine-like encryption to your python project. Also included is a simplistic "Hello World" proof of concept, a basic catalogue of rotors in the JSON format expected (`catalogue.json`), and a convenience script for preparing the catalogue from a csv.

## Security Notice

In the age of gigahertz pocket computing, the Enigma cipher is useful as a point of curiosity only. None of the original security flaws with the Enigma machine as patented have been corrected.

## Historical Accuracy Notice

While pains were taken to ensure the interoperability of this emulator and the actual enigma machine, nothing about the module enforces historical accuracy in terms of the use of particular parts or settings, or the "tidying" features of the operator.

In particular, this model allows for an arbitrary number of wheels to be used, some of which were not historically used together. All wheels obey an M3/M4-style "double stepping" movement pattern. The smoother gearbox stepping patterns of some later models are not emulated.

## Making use

The principle way to use the Enigma module in your scripts is to import and invoke the Enigma class. For convenience, you can read in the string "default" as the catalog list to use the stock catalog included in the module.

The Enigma class accepts the following arguments on initialization:

- catalog: a dictionary of rotor bindings, or the string "default" to use the stock bindings included in the module.
- stecker: A space-separated string of bindings to use for the steckerboard settings. Ex, "AB CD" means that stecker cables are set between A and B, and C and D.
- rotors: a list of tuples showing the rotor name from the catalog and the desired ringstellung letter setting, ex `[("III", "D"),]`. Any number of rotors may be used, including duplicates.
- reflector: a string indicating the name of the rotor from the rotor catalogue which you would like to use for the reflector, ex 'Reflector B'.
- operator: if True, the operator class will be used. This strips unprintable characters from the message and cuts the message into 5-character chunks.
- word_length: overrides the length of the words used by the operator.
- stator: accepts "military" or "civilian", to imitate either the direct encoding of the military version of the device or the QWERTZ encoding used in the civilian model.

Use of the Enigma class provides a variety of convenience methods:

- set_wheels: accepts a string of wheel positions (as read left to right) and applies them to be the message setting. Should be called before every parse call.
- set_stecker: if desirable, one could override the steckerboard settings after instantiating the entire machine.
- parse: parses the string provided and returns that message as though it were processed through an actual Enigma Machine.
