from dosbox import *
from dosbox.breaks import Breaks
from dosbox.plugins import Logger


class FileTrace(Logger):
    __metaclass__ = Singleton

    def __create__(self):
        Logger.__init__(self)
        self.handles = {}
        self._d = Dosbox()
        self.on = False
        self.trace = 0

    def hlog(self, log, hndl=None):
        if hndl:
            h = self.handles.get(hndl)
            self.log("%04X:%04X %s (h=%d pos=%d %s)", self._d.cs, self._d.ip, log, hndl, h[1], h[0])
        else:
            self.log("%04X:%04X %s", self._d.cs, self._d.ip, log)

    def mktrace(self, cnt=None):
        if cnt is None:
            cnt = self.trace
        if cnt == 0:
            if self.nonstop:
                self._d.cont()
            return
        self.hlog("\t <caller>")
        self._d.finish(callback=self.mktrace, cnt=cnt-1)

    def fopen(self, **kwargs):
        nm = readString()
        if self.fname and self.fname != nm:
            return True
        act = "create" if kwargs.get('value') == 0x3C else "open"
        def created(**kwargs):
            h = self._d.ax
            if isCarry():
                self.hlog("file {} failed {:04X}".format(act, h))
                return self.mktrace
            self.handles[h] = [nm, 0]
            self.hlog("file "+act, h)
            return self.mktrace
        self._d.next(created)

    def fclose(self, **kwargs):
        if not self._d.bx in self.handles:
            return
        bx = self._d.bx
        self.hlog("file closed", bx)
        del self.handles[bx]
        return self.mktrace

    def frw(self, **kwargs):
        h = self._d.bx
        if not h in self.handles:
            return
        act = "read" if kwargs.get('value') == 0x3F else "write"
        sz = self._d.cx
        buf = (self._d.ds << 4) + self._d.dx
        def readed(**kwargs):
            rd = self._d.ax
            if isCarry():
                self.hlog("file {} {} failed: {:04X}".format(act, sz, rd), h)
                return self.mktrace
            if self.dump:
                hexdump(self._d.mem(buf, rd), self.handles[h][1])
            self.handles[h][1] += rd
            self.hlog("file {} {} of {}".format(act, rd, sz), h)
            return self.mktrace
        self._d.next(readed)

    def fseek(self, **kwargs):
        h = self._d.bx
        if not h in self.handles:
            return True
        ln = (self._d.cx << 16) + self._d.dx
        pos = self._d.al
        def seeked(**kwargs):
            if isCarry():
                self.hlog("file seek failed {} from {}: {:04X}".format(ln, pos, self._d.ax), h)
                return self.mktrace()
            npos = (self._d.dx << 16) + self._d.ax
            self.handles[h][1] = npos
            self.hlog("file seek {} from {}".format(ln, pos), h)
            return self.mktrace()
        self._d.next(seeked)

    def unlink(self, **kwargs):
        nm = readString()
        if self.fname and self.fname != nm:
            return True
        self.hlog("file delete "+nm)
        self.mktrace()

    def run(self, fname=None, nonstop=None, dump=False, logfile=None, trace=0):
        self.fname = fname
        self.nonstop = nonstop
        self.dump = dump
        self.trace = trace
        self.setLogFile(logfile)
        if self.on:
            return
        b = Breaks()
        b.add("dos_fcreate", self.fopen)
        b.add("dos_fopen", self.fopen)
        b.add("dos_fclose", self.fclose)
        b.add("dos_fread", self.frw)
        b.add("dos_fwrite", self.frw)
        b.add("dos_fseek", self.fseek)
        b.add("dos_unlink", self.unlink)
        self.on = True

    def clear(self):
        b = Breaks()
        b.delete("dos_fcreate")
        b.delete("dos_fopen")
        b.delete("dos_fclose")
        b.delete("dos_fread")
        b.delete("dos_fwrite")
        b.delete("dos_fseek")
        b.delete("dos_unlink")
        self.on = False


def nofiletrace():
    FileTrace().clear()


def filetrace(fname=None, nonstop=False, logfile=None, dump=False, trace=0):
    return FileTrace().run(fname, nonstop, dump, logfile, trace)
