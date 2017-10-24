import _dbox
from classes import *
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
        self.dasm = None
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

            import importlib
            ui = args.ui
            if ui and ui != "dosbox":
                if not ui.startswith("ui."):
                    ui = "ui." + ui
                sys.modules[ui] = importlib.import_module(ui)

            dasm = 'internal' if args.dasm == 'dosbox' else args.dasm
            if not dasm.startswith("disasm."):
                dasm = "disasm." + dasm
            sys.modules[dasm] = importlib.import_module(dasm)

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
        if self.dasm is None:
            raise Exception("Disassembler not inited")
        if addr is None:
            addr = [var('ip'), var('cs')]
        return self.dasm.disasm(tolinear(addr), size, var('eip'))

    def __getattr__(self, attr): return var(attr)
