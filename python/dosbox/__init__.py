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
    REGS = ["eax", "ecx", "edx", "ebx", "esp", "ebp", "esi", "edi", "eip", "eflags", "cs", "ss", "ds", "es", "fs", "gs"]
    WREGS = ["ax", "cx", "dx", "bx", "sp", "bp", "si", "di", "ip", "flags"]
    BREGS = ["ah", "al", "ch", "cl", "dh", "dl", "bh", "bl"]

    def __init__(self):
        self.ui = None
        self.vars = {}
        try:
            sys.path.append(os.getcwd())
            parser = argparse.ArgumentParser()
            parser.add_argument('--loglevel', default="info")
            parser.add_argument('--ui', default="dosbox")
            args = parser.parse_args()
            logger.debug("initing w args: %s", str(args))

            levels = {"debug": logging.DEBUG, "info": logging.INFO, "warning": logging.WARNING, "error": logging.ERROR}
            logger.setLevel(levels[args.loglevel])

            if self.ui is None:
                sys.stdout = sys.stderr = _dbox.CDosboxLog()

        except Exception as e:
            self.ui = None
            logger.error("%s initing python: %s", str(e.__class__.__name__), str(e), exc_info=1)
            raw_input("Press Enter to continue...")

    def setVars(self):
        regs = _dbox.regs()
        for i in range(len(regs)):
            self.vars[self.REGS[i]] = regs[i]

    def loop(self):
        self.setVars()
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

    def reg(self, name):
        if name in self.WREGS:
            return self.vars['e' + name] & 0xFFFF
        if name in self.BREGS:
            v = self.vars['e' + name[0] + 'x']
            return v & 0xFF if name[1] == 'l' else (v >> 8) & 0xFF
        return self.vars[name]

    def __getattr__(self, attr):
        return self.reg(attr)
