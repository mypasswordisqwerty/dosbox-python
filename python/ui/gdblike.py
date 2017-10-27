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
            "continue": self.cont,
            "next": self.next,
            "step": self.step,
            "until": self.until,
            "display": self.display,
            "quit": self.quit,
        }
        self.display = {"instructions": 0}

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
        if self.display['instructions'] > 0:
            print "> "+Dosbox().disasm(count=self.display['instructions'])

    def cont(self):
        Dosbox().cont()

    def next(self, cnt=1):
        cnt = int(cnt)
        logger.debug("next %d", cnt)
        if cnt > 1:
            Dosbox().next(self.next, cnt=cnt-1)
            return True
        Dosbox().next()
        return True

    def step(self, cnt=1):
        Dosbox().step()

    def until(self):
        l = Dosbox().dasm().single()
        Breaks().add("cs:ip+"+str(l[1]), once=True)
        Dosbox().cont()

    def display(self, count, what):
        count = int(count)
        for x in self.display:
            if x.startswith(what):
                self.display[x] = count
                return
        raise Exception("Unknown display: "+what)

    def quit(self):
        raise SystemExit()

    def loop(self):
        self.printDisplay()
        try:
            ii = code.InteractiveInterpreter(globals())
            s = raw_input(">>> ")
            args = s.split()
            for x in self.CMDS:
                if x.startswith(args[0]):
                    proc = self.CMDS[x]
                    proc(*args[1:])
                    return
            while ii.runsource(s):
                s += "\n" + raw_input("... ")
        except SystemExit:
            Dosbox().exit()

currentUI = GdbLike()
