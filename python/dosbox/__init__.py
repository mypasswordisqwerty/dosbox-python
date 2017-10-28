import _dbox
from classes import *
import sys
import os
import argparse
import logging
from util import *
from breaks import *
from context import *
from program import *

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
        self.server = None
        self.callbacks = {}
        self.ctx = Context()
        try:
            sys.path.append(os.getcwd())
            parser = argparse.ArgumentParser()
            parser.add_argument('--path', default="")
            parser.add_argument('--loglevel', default="info")
            parser.add_argument('--ui', default="dosbox")
            parser.add_argument('--dasm', default="dosbox")
            parser.add_argument('--server', default="")
            parser.add_argument('--host', default="")
            parser.add_argument('--port', default="1234")
            args = parser.parse_args()

            self.path = args.path
            levels = {"debug": logging.DEBUG, "info": logging.INFO, "warning": logging.WARNING, "error": logging.ERROR}
            logger.setLevel(levels[args.loglevel])
            logger.debug("initing w args: %s %s", str(args), sys.argv)

            self.loadPlugins(globals())

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

            srv = args.server
            if srv:
                if not srv.startswith("server."):
                    srv = "server." + srv
                self.host = args.host
                self.port = args.port
                sys.modules[srv] = importlib.import_module(srv)

            if self.ui is None:
                sys.stdout = sys.stderr = _dbox.CDosboxLog()
        except BaseException as e:
            self.ui = None
            logger.error("%s: %s", str(e.__class__.__name__), str(e), exc_info=1)
            raw_input("Press Enter to continue...")
            sys.stdout = sys.stderr = _dbox.CDosboxLog()

    def loadPlugins(self, glob):
        for x in os.listdir(self.path):
            fname = os.path.join(self.path, x)
            if os.path.isfile(fname) and fname.endswith(".py"):
                glob[x[:-3]] = __import__(x[:-3])

    def loop(self):
        self.ctx.updateRegs(_dbox.regs())
        cont = False
        torun = self.callbacks
        self.callbacks = {}
        try:
            for x in torun:
                if x(**torun[x]) == True:
                    cont = True
        except Exception as e:
            logger.error(str(e), exc_info=1)
            cont = False
        if cont:
            self.cont()
            return 0
        if self.ui:
            self.ui.loop()
        return 0

    def runCommand(self, cmd):
        exec(cmd, globals(), locals())
        return 0

    def cont(self, callback=None, **kwargs):
        self.addCallback(callback, kwargs)
        _dbox.cont()

    def next(self, callback=None, **kwargs):
        self.addCallback(callback, kwargs)
        _dbox.next()

    def step(self, callback=None, **kwargs):
        self.addCallback(callback, kwargs)
        _dbox.step()

    def addCallback(self, callback, params=None):
        if not callback:
            return
        self.callbacks[callback] = params

    def exit(self): _dbox.exit()

    def firstMCB(self): return _dbox.firstMCB()

    def mem(self, addr=None, size=256):
        if addr is None:
            addr = "ds:dx"
        return _dbox.memory(self.ctx.linear(addr), size)

    def disasm(self, addr=None, count=10):
        if self.dasm is None:
            raise Exception("Disassembler not inited")
        if addr is None:
            addr = "cs:ip"
        return self.dasm.disasm(addr, count, self.ctx.eip)

    def __getattr__(self, attr): return self.ctx.eval(attr)
