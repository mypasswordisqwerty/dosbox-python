
from dosbox import *
from dosbox.classes import UI
import readline
import logging
import code
logger = logging.getLogger("dosbox.pureui")


class PureUI(UI):

    def __init__(self):
        UI.__init__(self)
        logging.debug("inited")

    def loop(self):
        logging.debug("loop")
        try:
            ii = code.InteractiveInterpreter(globals())
            s = raw_input(">>> ")
            while ii.runsource(s):
                s += "\n" + raw_input("... ")
        except SystemExit:
            Dosbox().exit()

Dosbox().ui = PureUI()
