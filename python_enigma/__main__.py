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
import webbrowser

# We really only need things to execute here if being called as main, such as `python -m python_enigma`


def test_button():  # TODO Remove when no longer relied upon
    print("Button Works!")
    return


def display_about_window():
    about_window = Toplevel(window)
    box = LabelFrame(about_window, text="About Python Enigma")
    about_blurb = "This is a toy project intending to implement the Enigma Machine as originally " \
                  "designed by Arthur Scherbius. Enigma was an electromechanical implementation of " \
                  "a polyalphabetic substitution cypher. It's no longer considered " \
                  "cryptographically secure, but the device itself was fairly interesting.\n\n" \
                  "No effort has been made to correct any of the cryptographic flaws in enigma; " \
                  "this implementation is meant to be as faithful as possible. Additionally, " \
                  "steps have been taken to attempt to emulate not just the Wehrmacht enigma, but " \
                  "the commercial models as well.\n\nFurther information is available using the links below." \
                  "\n\nThis is a work product of Kensho Security Labs," \
                  " provided under the Apache 2.0 License."
    box.grid(row=0, column=0)
    text = Message(box, text=about_blurb, width=500)
    text.pack()
    ks_button = Button(box, text="Kensho Security Labs", command=launch_kenshosec, width=15)
    gh_button = Button(box, text="Github Project Page", command=launch_github, width=15)
    gh_button.pack()
    ks_button.pack()


def fill_wheel_states():
    wheel_state_raw = machine_used.wheel_pack.rotors.copy()
    wheel_state_raw.reverse()  # wheels will now appear in visible order, as indexed.
    counter = 1
    for rotor in wheel_state_raw:  # we can iterate over these to start filling the parent.
        readable_pos = enigma.num_to_alpha(rotor.position)
        wheel_id = rotor.name
        ringstellung = rotor.ringstellung
        new_wheel = LabelFrame(wheel_states, width=25, height=25, text=("%s" % str(counter)))
        new_wheel.pack(side=LEFT)
        pos_var = StringVar()
        pos_var.set(readable_pos)
        pos_label = Label(new_wheel, text="Position:")
        pos_label.grid(row=0, column=0)
        wheel_label = Label(new_wheel, text="Wheel:")
        wheel_label.grid(row=0, column=1)
        wheel_position_setting = Entry(new_wheel, width=1, textvariable=pos_var)
        wheel_position_setting.grid_propagate(0)
        wheel_position_setting.grid(row=1, column=0)
        wheel_type = Label(new_wheel, text=wheel_id)
        wheel_type.grid(row=1, column=1)
        rings_label = Label(new_wheel, text="Ringstellung:")
        rings_setting = Label(new_wheel, text=ringstellung)
        rings_label.grid(row=2, column=0)
        rings_setting.grid(row=2, column=1)
        counter += 1

def initialize_stock_enigma():
    use_these = [("Beta", "A"), ("I", "A"), ("II", "A"), ("III", "A")]
    machine = enigma.Enigma(catalog="default", stecker=None, stator="military", rotors=use_these, reflector="UKW",
                            operator=True, word_length=5, ignore_static_wheels=False)
    return machine


def launch_kenshosec():
    webbrowser.open("https://www.kenshosec.com/Projects")
    return


def launch_github():
    webbrowser.open("https://www.github.com/ZAdamMac/python-enigma")
    return


if __name__ == "__main__":
    machine_used = initialize_stock_enigma()
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
    settings_pane = LabelFrame(window, text="Machine State", height=input_pane.winfo_height(), width=537)
    settings_pane.grid_propagate(0)
    settings_pane.grid(column=1, row=0)
    controls_pane = Frame(window)
    controls_pane.grid(column=1, row=1)

    # This code populates the various items that need to go in the settings pane
    # This pane uses grid geometry.
    wheel_selections = Button(settings_pane, command=test_button, text="Select Wheels")  # TODO Define Correct Command
    wheel_selections.grid_anchor(CENTER)
    wheel_selections.grid(column=0, row=0)
    stecker_config = Button(settings_pane, command=test_button, text="Steckerboard Config")
    stecker_config.grid_anchor(CENTER)
    stecker_config.grid(column=1, row=0)
    wheel_states = LabelFrame(settings_pane, text="Wheel States")
    wheel_states.grid_anchor(CENTER)
    #filler = Label(wheel_states, text="We don't fill this frame because that requires a function not yet defined!")
    wheel_states.grid(row=1, columnspan=2)
    wheel_states.grid_anchor(CENTER)
    fill_wheel_states()
    #filler.pack()

    # This code populates the various items that need to go in the controls pane!
    go_button = Button(controls_pane, text="Process Message", command=test_button, width=25)  # TODO The Do!
    reset_button = Button(controls_pane, text="Reset State", command=test_button, width=25)  # TODO def
    credits_button = Button(controls_pane, text="About python_enigma", command=display_about_window, width=25)
    go_button.grid(row=0)
    reset_button.grid(row=1)
    credits_button.grid(row=2)

    window.mainloop()
