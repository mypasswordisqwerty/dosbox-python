from dosbox import *
import os


class Ar(Program):

    def __init__(self):
        sym = os.path.join(os.path.dirname(__file__), "ar_sym.json")
        Program.__init__(self, "ar.exe", sym)

    def loaded(self):
        print "AR loaded at "+hex(self.base)
        Breaks().add("FREAD_START")
        Dosbox().cont()


prog = Ar()
