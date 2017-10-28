from dosbox import *
import readline
import code
import os
import atexit
import logging

logger = logging.getLogger("dosbox.gdblike")


class GdbLike(UI):

    def __init__(self):
        UI.__init__(self)
        readline.parse_and_bind("tab: complete")
        histfile = os.path.expanduser("~/.dosbox_hist")
        try:
            readline.read_history_file(histfile)
        except Exception:
            pass
        atexit.register(self.save_history, histfile)
        readline.set_completer(self.completer)
        self.CMDS = {
            "x": self.printMem,
            "continue": self.cont,
            "next": self.next,
            "step": self.step,
            "until": self.until,
            "finish": self.finish,
            "disassemble": self.disasm,
            "display": self.display,
            "info": self.info,
            "quit": self.quit,
        }
        self.DISPLAY = {"instructions": 0, "registers": 0}
        self.INFO = {"registers": self.infoRegs}
        self.inited = False

    def init(self):
        self.inited = True
        fl = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "gdblike_init"))
        if not os.path.isfile(fl):
            return
        for x in open(fl).readlines():
            self.procCmd(x)

    def save_history(self, histfile):
        readline.set_history_length(1000)
        readline.write_history_file(histfile)

    def completer(self, text, status):
        ret = []
        for x in self.CMDS:
            if x.startswith(text):
                ret += [x]
        return ret

    def printDisplay(self):
        if self.DISPLAY['registers'] > 0:
            self.info("reg")
            print
        if self.DISPLAY['instructions'] > 0:
            print ">",
            self.disasm(cnt=self.DISPLAY['instructions'])
            print

    def cont(self):
        Dosbox().cont()

    def next(self, cnt=1):
        cnt = int(cnt)
        logger.debug("next %d", cnt)
        if cnt > 1:
            Dosbox().next(self.next, cnt=cnt-1)
        else:
            Dosbox().next()

    def step(self, cnt=1):
        cnt = int(cnt)
        logger.debug("next %d", cnt)
        if cnt > 1:
            Dosbox().step(self.step, cnt=cnt-1)
        else:
            Dosbox().step()

    def until(self):
        Dosbox().until()

    def finish(self):
        Dosbox().finish()

    def disasm(self, where="cs:ip", cnt=10):
        cnt = int(cnt)
        print Dosbox().disasm(where, cnt)

    def info(self, what, *how):
        for x in self.INFO:
            if x.startswith(what):
                self.INFO[x](*how)
                return
        raise Exception("Unknown info: "+what)

    def infoRegs(self, *args):
        ret = ""
        ctx = Context()
        for x in context.WREGS[:-1]:
            ret += "{}={:04X} ".format(x, ctx.var(x))
        ret += "\nflags={:04X} cs={:04X} ds={:04X} es={:04X} ss={:04X}".format(ctx.flags,
                                                                               ctx.cs, ctx.ds, ctx.es, ctx.ss)
        print ret

    def printMem(self, addr="ds:dx", size=32):
        size = int(size)
        hexdump(Dosbox().mem(addr, size), addr)

    def display(self, what, count=5):
        count = int(count)
        for x in self.DISPLAY:
            if x.startswith(what):
                self.DISPLAY[x] = count
                return
        raise Exception("Unknown display: "+what)

    def quit(self):
        raise SystemExit()

    def procCmd(self, cmd):
        args = cmd.split()
        for x in self.CMDS:
            if x.startswith(args[0]):
                proc = self.CMDS[x]
                proc(*args[1:])
                return True
        return False

    def loop(self):
        if not self.inited:
            self.init()
        self.printDisplay()
        try:
            ii = code.InteractiveInterpreter(globals())
            s = raw_input(">>> ")
            if self.procCmd(s):
                return
            while ii.runsource(s):
                s += "\n" + raw_input("... ")
        except SystemExit:
            Dosbox().exit()

currentUI = GdbLike()
