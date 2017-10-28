from dosbox import *
import logging

logger = logging.getLogger("dosbox.program")


class Program:
    """ Debugged program base class """

    def __init__(self, fname, symbols=None):
        self.fname = fname.lower()
        self.symbols = symbols
        self.psp = self._checkLoaded()
        self.base = None
        if self.psp:
            if self._prepare():
                Dosbox().cont()
        else:
            Breaks().addExec(callback=self._onExec)

    def _onExec(self, **kwargs):
        psp = kwargs.get('value')
        nm = readEnv(psp, True)
        logger.debug("check exec %s", nm)
        if nm.lower().endswith(self.fname):
            self.psp = psp
            Breaks().delExec()
            return self._prepare()
        else:
            return True

    def _prepare(self):
        self.base = self.psp+0x10
        if self.symbols:
            logger.debug("loading symbols from %s at %04X", self.symbols, self.base)
            Context().loadSymbols(self.fname, self.base)
        return self.loaded()

    def _checkLoaded(self):
        prg = loadedProgs()
        for x in prg:
            if not prg[x]:
                continue
            if prg[x].lower().endswith(self.fname):
                return x
        return None

    def loaded(self):
        """ called on program load"""
        logger.info("Program %s loaded at %04X", self.fname, self.base)
        return False
