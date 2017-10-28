from dosbox import *
import os


class Ar(Program):

    def __init__(self):
        sym = os.path.join(os.path.dirname(__file__), "ar_sym.json")
        Program.__init__('ar.exe', sym)

    def loaded(self, **kwargs):
        print "AR loaded"


prog = Ar()
