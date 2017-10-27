import _break
from util import *
import dosbox
from context import Context
from classes import Singleton
import logging

logger = logging.getLogger("dosbox.breaks")


class Breaks:
    __metaclass__ = Singleton

    def __create__(self):
        self.callbacks = {}
        self.ctx = Context()

    def brk2hash(self, brk):
        return {"location": brk.GetLocation(), "seg": brk.GetSegment(), "ofs": brk.GetOffset(),
                "intNr": brk.GetIntNr(), "value": brk.GetValue()}

    def run(self, brk):
        bid = brk.GetId()
        logger.debug("Breakpoint run %s %d", str(brk), bid)
        if bid in self.callbacks:
            dosbox.Dosbox().addCallback(self.callbacks[bid], self.brk2hash(brk))
            if brk.GetOnce():
                del self.callbacks[bid]

    def show(self):
        _break.ShowList()

    def getlist(self):
        return _break.List()

    def _addBreak(self, brk, callback=None):
        if callback:
            self.callbacks[brk.GetId()] = callback
        return brk

    def addAddr(seg, ofs, allback=None, once=False):
        return Breaks()._addBreak(_break.AddBreakpoint(seg, ofs, once), callback)

    def addInt(self, intNr, ah=None, callback=None, once=False):
        return Breaks()._addBreak(_break.AddIntBreakpoint(intNr, ah or 0, once), callback)

    def addMem(self, seg, ofs, callback=None):
        return Breaks()._addBreak(_break.AddMemBreakpoint(seg, ofs), callback)

    def addExec(self, callback=None, once=False):
        return Breaks()._addBreak(_break.AddExecBreakpoint(once), callback)

    def add(self, sym, callback=None, once=False):
        addr = self.ctx.eval(sym)
        if isinstance(addr, dict):
            return self.addInt(addr['int'], addr.get('ah'), callback, once)
        return self.addAddr(addr[0], addr[1], callback, once)

    def clear(self, index):
        _break.DeleteAll()

    def delete(self, sym):
        addr = self.ctx.eval(sym)
        if isinstance(addr, dict):
            self.delInt(addr['int'], addr.get('ah'))
        else:
            self.delAddr(addr[0], addr[1])

    def delIndex(self, index):
        lst = self.getlist()
        if len(lst) > index:
            b = lst[index]
            if b.GetId() in self.callbacks:
                del self.callbacks[b.GetId()]
        _break.DeleteByIndex(index)

    def delAddr(self, seg, ofs):
        for i, b in enumerate(self.getlist()):
            if b.GetSegment() == seg and b.GetOffset() == ofs:
                self.delIndex(i)
                return

    def delInt(self, intNr, ah=None):
        ah = ah or 0
        for i, b in enumerate(self.getlist()):
            if b.GetIntNr() == intNr and b.GetValue() == ah:
                self.delIndex(i)
                return

    def delExec(self):
        for i, b in enumerate(self.getlist()):
            if b.NAMES[b.GetType] == "EXEC":
                self.delIndex(i)
                return
