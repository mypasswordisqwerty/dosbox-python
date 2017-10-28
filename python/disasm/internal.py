from dosbox import Disasm
from dosbox.context import Context
import _dbox


class DosboxDisasm(Disasm):

    def __init__(self):
        Disasm.__init__(self)
        self.ctx = Context()

    def single(self, addr="cs:ip"):
        return _dbox.disasm(self.ctx.linear(addr), self.ctx.eip)

    def disasm(self, addr, count, eip):
        ret = ''
        ad = self.ctx.addr(addr)
        seg = ad[0]
        lseg = ad[0] << 4
        loc = lseg + ad[1]
        for i in range(count):
            l = _dbox.disasm(loc, eip)
            ret += "\n{}{:04X}:{:04X}\t{}".format(self.ctx.name(loc), seg, loc-lseg, l[0])
            loc += l[1]
        return ret[1:]


currentDasm = DosboxDisasm()
