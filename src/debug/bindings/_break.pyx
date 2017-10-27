from libcpp cimport bool
from libcpp.list cimport list

cdef extern from "dosbox.h":
    ctypedef unsigned char Bit8u
    ctypedef unsigned short Bit16u
    ctypedef unsigned int Bit32u
    ctypedef unsigned long long Bit64u
    ctypedef unsigned int PhysPt
    ctypedef Bit64u Bitu


cdef extern from "../debug.hpp":
    ctypedef enum EBreakpoint:
        BKPNT_UNKNOWN, BKPNT_PHYSICAL, BKPNT_INTERRUPT, BKPNT_MEMORY, BKPNT_MEMORY_PROT, BKPNT_MEMORY_LINEAR, BKPNT_EXEC
    cdef cppclass CBreakpoint:
        CBreakpoint() except +
        void SetAddress(Bit16u seg, Bit32u off)
        void SetAddress(PhysPt adr)
        void SetInt(Bit8u _intNr, Bit16u ah)
        void SetOnce(bool _once)
        void SetType(EBreakpoint _type)
        bool IsActive()
        void Activate(bool _active)
        EBreakpoint GetType()
        bool GetOnce()
        PhysPt GetLocation()
        Bit16u GetSegment()
        Bit32u GetOffset()
        Bit8u GetIntNr()
        Bit16u GetValue()
        unsigned int GetId()

        @staticmethod
        CBreakpoint * AddBreakpoint(Bit16u seg, Bit32u off, bool once)

        @staticmethod
        CBreakpoint * AddIntBreakpoint(Bit8u intNum, Bit16u ah, bool once)

        @staticmethod
        CBreakpoint * AddMemBreakpoint(Bit16u seg, Bit32u off)

        @staticmethod
        CBreakpoint * AddExecBreakpoint(bool once)

        @staticmethod
        bool DeleteBreakpoint(PhysPt where)

        @staticmethod
        bool DeleteByIndex(Bit16u index)

        @staticmethod
        void DeleteAll()

        @staticmethod
        void ShowList()

cdef extern from "../debug.hpp" namespace "CBreakpoint":
    list[CBreakpoint * ] BPoints


_BREAKS = None

cdef class PyBreakpoint:
    cdef CBreakpoint * c_bp
    NAMES = ["UNKNOWN", "PHYSICAL", "INTERRUPT", "MEMORY", "MEMORY_PROT", "MEMORY_LINEAR", "EXEC"]

    cdef __setp__(self, CBreakpoint * bp):
        self.c_bp = bp
        return self

    def SetAddress(self, unsigned long seg, off=None):
        if off:
            self.c_bp.SetAddress(seg, off)
        else:
            self.c_bp.SetAddress(seg)

    def SetInt(self, Bit8u _intNr, Bit16u ah): self.c_bp.SetInt(_intNr, ah)

    def SetOnce(self, bool _once): self.c_bp.SetOnce(_once)

    def SetType(self, EBreakpoint _type): self.c_bp.SetType(_type)

    def IsActive(self): return self.c_bp.IsActive()

    def Activate(self, bool _active): self.c_bp.Activate(_active)

    def GetType(self): return self.c_bp.GetType()

    def GetOnce(self): return self.c_bp.GetOnce()

    def GetLocation(self): return self.c_bp.GetLocation()

    def GetSegment(self): return self.c_bp.GetSegment()

    def GetOffset(self): return self.c_bp.GetOffset()

    def GetIntNr(self): return self.c_bp.GetIntNr()

    def GetValue(self): return self.c_bp.GetValue()

    def GetId(self): return self.c_bp.GetId()

    def __repr__(self):
        tp = self.GetType()
        ret = "<"+self.NAMES[tp]
        if tp == BKPNT_INTERRUPT:
            ret += " %02X %02X" % (self.GetIntNr(), self.GetValue())
        else:
            ret += " %04X:%04X" % (self.GetSegment(), self.GetOffset())
        return ret+">"


cdef public int break_run(CBreakpoint * brk):
    global _BREAKS
    if not _BREAKS:
        import dosbox.breaks
        _BREAKS = dosbox.breaks.Breaks()
    _BREAKS.run(PyBreakpoint().__setp__(brk))


def AddBreakpoint(Bit16u seg, Bit32u off, bool once):
    return PyBreakpoint().__setp__(CBreakpoint.AddBreakpoint(seg, off, once))


def AddIntBreakpoint(Bit8u intNum, Bit16u ah, bool once):
    return PyBreakpoint().__setp__(CBreakpoint.AddIntBreakpoint(intNum, ah, once))


def AddMemBreakpoint(Bit16u seg, Bit32u off):
    return PyBreakpoint().__setp__(CBreakpoint.AddMemBreakpoint(seg, off))


def AddExecBreakpoint(bool once):
    return PyBreakpoint().__setp__(CBreakpoint.AddExecBreakpoint(once))


def DeleteBreakpoint(PhysPt where):
    return CBreakpoint.DeleteBreakpoint(where)


def DeleteByIndex(Bit16u index):
    return CBreakpoint.DeleteByIndex(index)


def DeleteAll():
    CBreakpoint.DeleteAll()


def ShowList():
    CBreakpoint.ShowList()


def GetBreak(bid):
    for bp in BPoints:
        if bp.GetId() == bid:
            return PyBreakpoint().__setp__(bp)
    return None


def List():
    ret = []
    for bp in BPoints:
        ret += [PyBreakpoint().__setp__(bp)]
    return ret
