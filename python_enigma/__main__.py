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

Development was by Zac Adam-MacEwen. See the README.md for details.

"""

__version__ = "1.2.0Dev"

from . import enigma
from tkinter import *

# We really only need things to execute here if being called as main, such as `python -m python_enigma`


def test_button():
    print("Button Works!")
    return

if __name__ == "__main__":
    # TODO DEF "fetch Stock Enigma"
    window = Tk()
    window.title("Python Enigma v.%s" % __version__)
    # this code block draws the window itself.
    input_pane = LabelFrame(window, text="Input")
    input_pane.grid(column=0, row=0)
    input_field = Text(input_pane, width=80, height=24)
    input_field.pack()
    output_pane = LabelFrame(window, text="Output")
    output_pane.grid(column=0, row=1)
    output_field = Text(output_pane, width=80, height=24)
    output_field.pack()
    window.update()  # Needed because we're taking some dynamic sizes!
    settings_pane = LabelFrame(window, text="Machine State", height=input_pane.winfo_height(), width=450)
    settings_pane.grid_propagate(0)
    settings_pane.grid(column=1, row=0)
    controls_pane = Frame(window)
    controls_pane.grid(column=1, row=1)

    # This code populates the various items that need to go in the settings pane
    # This pane uses grid geometry.
    wheel_selections = Button(settings_pane, command=test_button, text="Select Wheels")  # TODO Define Correct Command
    wheel_selections.grid(column=0, row=0)
    stecker_config = Button(settings_pane, command=test_button, text="Steckerboard Config")
    stecker_config.grid(column=1, row=0)
    wheel_states = LabelFrame(settings_pane, text="Wheel States")
    filler = Label(wheel_states, text="We don't fill this frame because that requires a function not yet defined!")
    wheel_states.grid(row=1, columnspan=2)
    # TODO DEF - Fill_Wheel_States
    filler.pack()

    # This code populates the various items that need to go in the controls pane!
    go_button = Button(controls_pane, text="Process Message", command=test_button, width=25)  # TODO The Do!
    reset_button = Button(controls_pane, text="Reset State", command=test_button, width=25)  # TODO def
    credits_button = Button(controls_pane, text="Credits", command=test_button, width=25)  # TODO def!
    go_button.grid(row=0)
    reset_button.grid(row=1)
    credits_button.grid(row=2)

    window.mainloop()
