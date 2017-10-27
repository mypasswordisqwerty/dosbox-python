
from dosbox import *
import readline
import code
import os
import atexit


class PureUI(UI):

    def __init__(self):
        UI.__init__(self)
        # Dosbox().loadPlugins(globals())
        readline.parse_and_bind("tab: complete")
        histfile = os.path.expanduser("~/.dosbox_hist")
        try:
            readline.read_history_file(histfile)
        except Exception:
            pass
        atexit.register(self.save_history, histfile)

    def save_history(self, histfile):
        readline.set_history_length(1000)
        readline.write_history_file(histfile)

    def loop(self):
        try:
            ii = code.InteractiveInterpreter(globals())
            s = raw_input(">>> ")
            if s in ["exit", "quit", "q"]:
                raise SystemExit()
            while ii.runsource(s):
                s += "\n" + raw_input("... ")
        except SystemExit:
            Dosbox().exit()

currentUI = PureUI()
