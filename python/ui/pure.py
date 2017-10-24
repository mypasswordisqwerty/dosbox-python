
from dosbox import Dosbox, UI
import readline
import logging
import code


class PureUI(UI):

    def loop(self):
        try:
            ii = code.InteractiveInterpreter(globals())
            s = raw_input(">>> ")
            while ii.runsource(s):
                s += "\n" + raw_input("... ")
        except SystemExit:
            Dosbox().exit()

currentUI = PureUI()
