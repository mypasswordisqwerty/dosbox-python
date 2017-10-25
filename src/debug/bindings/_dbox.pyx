cdef extern from "dosbox.h":
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

cdef extern from "paging.h":
    int mem_readb_checked(unsigned int address, unsigned char * val)

cdef extern from "debug_api.h":
    cdef void DEBUG_ShowMsg(char * format, char * )
    cdef void DEBUG_Continue()
    cdef void DEBUG_Next()
    cdef void DEBUG_Step()
    cdef int PYTHON_Command(const char * cmd)
    cdef char * PYTHON_Dasm(unsigned int ptr, unsigned int eip, int & size)


cdef _DOSBOX = None


# logger
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


# cpp routines
cdef public int dbox_start():
    global _DOSBOX
    try:
        from dosbox import Dosbox
        _DOSBOX = Dosbox()
    except Exception as e:
        import traceback
        print "FATAL: " + str(e.__class__.__name__) + ": " + str(e)
        traceback.print_exc()
        raw_input("Press ENTER to abort...")
        exit()
    return _DOSBOX.ui is not None

cdef public int dbox_loop():
    return _DOSBOX.loop()

cdef public int dbox_exec(const char * cmd):
    return _DOSBOX.runCommand(cmd)


# py routines
def exit(): PYTHON_Command(NULL)


def cont(): DEBUG_Continue()


def next(): DEBUG_Next()


def step(): DEBUG_Step()


def regs():
    return [reg_eax, reg_ecx, reg_edx, reg_ebx, reg_esp, reg_ebp, reg_esi, reg_edi, reg_eip,
            reg_flags, SegValue(cs), SegValue(ss), SegValue(ds), SegValue(es), SegValue(fs), SegValue(gs)]


def memory(int loc, int size):
    ret = ''
    cdef unsigned char v
    for i in range(size):
        if mem_readb_checked(loc, & v) != 0:
            v = 0
        ret += chr(v)
        loc += 1
    return ret


def disasm(int loc, int eip):
    cdef int sz = 0
    val = PYTHON_Dasm(loc, eip, sz)
    return (val, sz)
