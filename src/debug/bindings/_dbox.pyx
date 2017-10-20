
cdef extern from "dosbox.h":
    pass

cdef extern from "../debug_api.h":
    cdef void DEBUG_ShowMsg(char * format, char*)
    cdef void DEBUG_Run()
    cdef void DEBUG_StepOver()
    cdef void DEBUG_StepInto()

cdef public char * version = "0.1"

class CDosboxLog:
    def __init__(self):
        self.buf = ''

    def write(self, s):
        if s[-1]=='\n':
            self.buf += s[:-1]
            self.flush()
        else:
            self.buf += s;

    def flush(self):
        DEBUG_ShowMsg("%s", self.buf)
        self.buf = ''

def run():
    DEBUG_Run();

def stepOver():
    DEBUG_StepOver();

def stepInto():
    DEBUG_StepInto();
