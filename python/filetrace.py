from dosbox import *
from dosbox.breaks import Breaks


class FileTrace:

    def __init__(self, fname=None, nonstop=None, dump=False):
        self.fname = fname
        self.handles = {}
        self._d = Dosbox()
        self.nonstop = nonstop
        self.dump = dump

    def log(self, log, hndl=None):
        if hndl:
            h = self.handles.get(hndl)
            print "{:04X}:{:04X} {} (h={} pos={} {})".format(self._d.cs, self._d.ip, log, hndl, h[1], h[0])
        else:
            print "{:04X}:{:04X} {}".format(self._d.cs, self._d.ip, log)

    def fopen(self, **kwargs):
        nm = readString()
        if self.fname and self.fname != nm:
            return True
        act = "create" if kwargs.get('value') == 0x3C else "open"
        def created(**kwargs):
            h = self._d.ax
            if isCarry():
                self.log("file {} failed {:04X}".format(act, h))
                return self.nonstop
            self.handles[h] = [nm, 0]
            self.log("file "+act, h)
            return self.nonstop
        self._d.next(created)
        return True

    def fclose(self, **kwargs):
        if not self._d.bx in self.handles:
            return True
        bx = self._d.bx
        self.log("file closed", bx)
        del self.handles[bx]
        return self.nonstop

    def frw(self, **kwargs):
        h = self._d.bx
        if not h in self.handles:
            return True
        act = "read" if kwargs.get('value') == 0x3F else "write"
        self.log("file "+act, h)
        return self.nonstop

    def fseek(self, **kwargs):
        h = self._d.bx
        if not h in self.handles:
            return True
        ln = (self._d.cx << 16) + self._d.dx
        pos = self._d.al
        def seeked(**kwargs):
            if isCarry():
                self.log("file seek failed {} from {}".format(ln, pos), h)
                return self.nonstop
            npos = (self._d.dx << 16) + self._d.ax
            self.handles[h][1] = npos
            self.log("file seek {} from {}".format(ln, pos), h)
            return self.nonstop
        self._d.next(seeked)
        return True

    def unlink(self, **kwargs):
        nm = readString()
        if self.fname and self.fname != nm:
            return True
        self.log("file delete "+nm)
        return self.nonstop

    def run(self):
        b = Breaks()
        b.add("dos_fcreate", self.fopen)
        b.add("dos_fopen", self.fopen)
        b.add("dos_fclose", self.fclose)
        b.add("dos_fread", self.frw)
        b.add("dos_fwrite", self.frw)
        b.add("dos_fseek", self.fseek)
        b.add("dos_unlink", self.unlink)

    def clear(self):
        b = Breaks()
        b.delete("dos_fcreate")
        b.delete("dos_fopen")
        b.delete("dos_fclose")
        b.delete("dos_fread")
        b.delete("dos_fwrite")
        b.delete("dos_fseek")
        b.delete("dos_unlink")


def nofiletrace():
    FileTrace().clear()


def filetrace(fname=None, nonstop=False, dump=False):
    nofiletrace()
    return FileTrace(fname, nonstop).run()
