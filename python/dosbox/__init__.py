import _dbox
import singleton
import sys
import os
import argparse
import logging
from util import *

__version__ = "dosbox v0.1"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("dosbox")


class Dosbox:
    __metaclass__ = singleton.Singleton

    def __init__(self):
        self.ui = None
        try:
            sys.path.append(os.getcwd())
            parser = argparse.ArgumentParser()
            parser.add_argument('--loglevel', default="info")
            parser.add_argument('--ui', default="dosbox")
            args = parser.parse_args()
            logger.debug("initing w args: %s", str(args))

            levels = {"debug": logging.DEBUG, "info": logging.INFO, "warning": logging.WARNING, "error": logging.ERROR}
            logger.setLevel(levels[args.loglevel])

            if args.ui:

            if self.ui is None:
                sys.stdout = sys.stderr = _dbox.CDosboxLog()

        except Exception as e:
            self.ui = None
            logger.error("%s initing python: %s", str(e.__class__.__name__), str(e), exc_info=1)
            raw_input("Press Enter to continue...")

    def loop(self):
        if self.ui:
            self.ui.loop()
        # breaks proc
        return 0

    def runCommand(self, cmd):
        exec(cmd, globals(), locals())
        return 0

    def cont(self): _dbox.cont()

    def next(self): _dbox.next()

    def step(self): _dbox.step()
