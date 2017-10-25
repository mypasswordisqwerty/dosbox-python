import _break
from util import *

from classes import Singleton


class Breaks:
    __metaclass__ = Singleton

    def __create__(self):
        self.callbacks = {}

    def run(self, brk):
        print "BP runned "+str(brk)

    def show(self):
        _break.ShowList()

    def getlist(self):
        return _break.List()

    def _addBreak(self, brk, callback=None):
        if callback:
            self.callbacks[brk.GetId()] = callback
        return brk

    @staticmethod
    def add(seg, ofs, once=False, callback=None):
        return Breaks()._addBreak(_break.AddBreakpoint(seg, ofs, once), callback)

    @staticmethod
    def addInt(intNr, ah=0, once=False, callback=None):
        return Breaks()._addBreak(_break.AddIntBreakpoint(intNr, ah, once), callback)

    @staticmethod
    def addMem(seg, ofs, callback=None):
        return Breaks()._addBreak(_break.AddMemBreakpoint(seg, ofs), callback)

    @staticmethod
    def addExec(once=False, callback=None):
        return Breaks()._addBreak(_break.AddExecBreakpoint(once), callback)
