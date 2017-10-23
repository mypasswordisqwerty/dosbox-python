
from dosbox import Debugger, IUI
import readline
import logging
logger = logging.getLogger("dosbox.pureui")


class PureUI(IUI):

    def __init__(self):
        logging.debug("inited")

    def loop(self):
        logging.debug("loop")
        s = input('>>> ')
        exec(s)


Debugger().ui = PureUI()
