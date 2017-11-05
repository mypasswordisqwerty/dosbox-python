from dosbox import *
import os
import logging
import struct
logger = logging.getLogger("dosbox.AR")


class Ar(Program):

    def __init__(self):
        sym = os.path.join(os.path.dirname(__file__), "ar_sym.json")
        Program.__init__(self, "ar.exe", sym)
        self.files = None

    def readFiles(self):
        fls = struct.unpack("<61H", self.mem("FILE_TABLE", 2*61))
        self.files = []
        for x in fls:
            f = struct.unpack("<13sB5H", self.dmem(x, 24))
            f = [f[0].rstrip("\x00"), f[1], [hex(f[2]), hex(f[3])], f[4], [hex(f[5]), hex(f[6])]]
            self.files += [f]
        logger.debug("Ar files: %s", str(self.files))

    def loaded(self):
        logger.info("AR loaded at %04X", self.base)
        self.readFiles()
        Breaks().add("FILE_UNPACK", self.unpack)
        Dosbox().cont()

    def unpack(self, **kwargs):
        logger.info("unpacking file")


prog = Ar()
