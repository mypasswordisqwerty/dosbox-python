cdef extern from "dosbox.h":
    pass

cdef extern from "../debug_api.h":
    cdef void DEBUG_ShowMsg(char * format, char * )
    cdef void DEBUG_Continue()
    cdef void DEBUG_Next()
    cdef void DEBUG_Step()
    ctypedef enum SegNames:
        es = 0, cs, ss, ds, fs, gs
    cdef unsigned short SegValue(SegNames s)
    cdef unsigned int reg_eax
    cdef unsigned int reg_ebx
    cdef unsigned int reg_ecx
    cdef unsigned int reg_edx
    cdef unsigned int reg_esi
    cdef unsigned int reg_edi
    cdef unsigned int reg_esp
    cdef unsigned int reg_ebp
    cdef unsigned int reg_eip
    cdef unsigned long reg_flags

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


def regs():
    return [reg_eax, reg_ecx, reg_edx, reg_ebx, reg_esp, reg_ebp, reg_esi, reg_edi, reg_eip,
            reg_flags, SegValue(cs), SegValue(ss), SegValue(ds), SegValue(es), SegValue(fs), SegValue(gs)]
