cdef extern from "dosbox.h":
    pass

cdef extern from "../debug_api.h":
    cdef void DEBUG_ShowMsg(char * format, char * )
    cdef void DEBUG_Continue()
    cdef void DEBUG_Next()
    cdef void DEBUG_Step()

cdef public char * version = "0.1"

cdef _DOSBOX = None


# cpp routines
cdef public int dbox_start():
    global _DOSBOX
    from dosbox import Dosbox
    _DOSBOX = Dosbox()
    return _DOSBOX.ui is not None

cdef public int dbox_loop():
    return _DOSBOX.loop()

cdef public int dbox_exec(const char * cmd):
    return _DOSBOX.runCommand(cmd)


# py routines
class CDosboxLog:

    def __init__(self):
        self.buf = ''

    def write(self, s):
        if s[-1] == '\n':
            self.buf += s[:-1]
            self.flush()
        else:
            self.buf += s

    def flush(self):
        DEBUG_ShowMsg("%s", self.buf)
        self.buf = ''


def cont():
    DEBUG_Continue()


def next():
    DEBUG_Next()


def step():
    DEBUG_Step()
