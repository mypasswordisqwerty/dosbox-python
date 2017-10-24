import _dbox
from classes import Singleton
import sys
import os
import argparse
import logging
from util import *

__version__ = "dosbox v0.1"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("dosbox")


class Dosbox(object):
    __metaclass__ = Singleton

    def __init__(self):
        pass

    def __create__(self):
        self.ui = None
        try:
            sys.path.append(os.getcwd())
            parser = argparse.ArgumentParser()
            parser.add_argument('--path', default="")
            parser.add_argument('--loglevel', default="info")
            parser.add_argument('--ui', default="dosbox")
            parser.add_argument('--dasm', default="dosbox")
            args = parser.parse_args()

            levels = {"debug": logging.DEBUG, "info": logging.INFO, "warning": logging.WARNING, "error": logging.ERROR}
            logger.setLevel(levels[args.loglevel])
            logger.debug("initing w args: %s %s", str(args), sys.argv)

            if args.ui and args.ui != 'dosbox':
                import importlib
                sys.modules[args.ui] = importlib.import_module(args.ui)

            if self.ui is None:
                sys.stdout = sys.stderr = _dbox.CDosboxLog()
        except BaseException as e:
            self.ui = None
            logger.error("%s: %s", str(e.__class__.__name__), str(e), exc_info=1)
            raw_input("Press Enter to continue...")
            sys.stdout = sys.stderr = _dbox.CDosboxLog()

    def loop(self):
        setRegs(_dbox.regs())
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

    def exit(self): _dbox.exit()

    def mem(self, addr=None, size=100):
        if addr is None:
            addr = [var('dx'), var('ds')]
        return _dbox.memory(tolinear(addr), size)

    def disasm(self, addr=None, size=10):
        ip = var('eip')
        addr = addr or [ip, var('cs')]
        return _dbox.disasm(tolinear(addr), ip)

    def __getattr__(self, attr): return var(attr)
