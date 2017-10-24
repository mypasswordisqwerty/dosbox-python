from dosbox import Disasm
import _dbox


class DosboxDisasm(Disasm):

    def disasm(self, loc, size, eip):
        ret = ''
        for i in range(size):
            l = _dbox.disasm(loc, eip)
            ret += "\n" + l[0]
            loc += l[1]
        return ret[1:]


currentDasm = DosboxDisasm()
