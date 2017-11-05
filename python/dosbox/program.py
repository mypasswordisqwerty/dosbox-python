import dosbox
import logging
import breaks
import context

logger = logging.getLogger("dosbox.program")


class Program:
    """ Debugged program base class """

    def __init__(self, fname, symbols=None):
        self.fname = fname.lower()
        self.symbols = symbols
        self.psp = self._checkLoaded()
        self.base = None
        self.dseg = None
        if self.psp:
            if self._prepare():
                dosbox.Dosbox().cont()
        else:
            breaks.Breaks().addExec(callback=self._onExec)

    def _onExec(self, **kwargs):
        psp = kwargs.get('value')
        nm = dosbox.readEnv(psp, True)
        logger.debug("check exec %s", nm)
        if nm.lower().endswith(self.fname):
            self.psp = psp
            breaks.Breaks().delExec()
            self._prepare()
        else:
            dosbox.Dosbox().cont()

    def _prepare(self):
        self.base = self.psp+0x10
        if self.symbols:
            logger.debug("loading symbols from %s at %04X", self.symbols, self.base)
            self.ctx = context.Context()
            self.ctx.loadSymbols(self.symbols, self.base)
            try:
                self.dseg = self.ctx.var("__SEG__DATA0")
            except Exception:
                self.dseg = None
        self.dbox = dosbox.Dosbox()
        self.loaded()

    def _checkLoaded(self):
        try:
            # check dosbox loaded/we are not plugin
            dosbox.Dosbox().cs
        except:
            return None
        prg = dosbox.loadedProgs()
        for x in prg:
            if not prg[x]:
                continue
            if prg[x].lower().endswith(self.fname):
                return x
        return None

    def loaded(self):
        """ called on program load"""
        logger.info("Program %s loaded at %04X", self.fname, self.base)

    def mem(self, sym, size=256):
        return self.dbox.mem(sym, size)

    def dmem(self, ofs, size):
        return self.mem([self.dseg, ofs], size)
