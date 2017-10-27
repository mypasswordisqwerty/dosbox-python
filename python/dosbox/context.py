from classes import Singleton
import binascii
import struct
import os
import json

REGS = ["eax", "ecx", "edx", "ebx", "esp", "ebp", "esi", "edi", "eip", "eflags", "cs", "ss", "ds", "es", "fs", "gs"]
WREGS = ["ax", "cx", "dx", "bx", "sp", "bp", "si", "di", "ip", "flags"]
BREGS = ["ah", "al", "ch", "cl", "dh", "dl", "bh", "bl"]
_FMTS = [None, '>B', '>H', None, '>I', None, None, None, '>Q']


class Context:
    __metaclass__ = Singleton

    def __create__(self):
        self._vars = {}
        self.path = os.path.realpath(os.path.join(os.path.dirname(__file__), ".."))
        self.loadSymbols(os.path.join(self.path, "data", "dos_sym.json"))

    def updateRegs(self, regs):
        for i in range(len(regs)):
            self._vars[REGS[i]] = regs[i]

    def setVar(self, name, val):
        self._vars[name] = val

    def setVars(self, vars):
        self._vars.update(vars)

    def loadSymbols(self, fname, segAdd=0):
        with open(fname) as f:
            data = json.load(f)
        for x in data:
            val = self.eval(data[x])
            if isinstance(val, (tuple, list)):
                val = [self.eval(x) for x in val]
                val[0] += segAdd
            if isinstance(val, dict):
                val = {k: self.eval(v) for k, v in val.iteritems()}
            self.setVar(x, val)

    def var(self, name):
        if name in self._vars:
            return self._vars[name]
        if name in WREGS:
            return self._vars['e' + name] & 0xFFFF
        if name in BREGS:
            v = self._vars['e' + name[0] + 'x']
            return v & 0xFF if name[1] == 'l' else (v >> 8) & 0xFF
        v = binascii.unhexlify(name)
        return struct.unpack(_FMTS[len(v)], v)[0]

    def __getattr__(self, attr):
        return self.var(attr)

    def __getitem__(self, attr):
        return self.var(attr)

    def eval(self, expr):
        if not isinstance(expr, basestring):
            return expr
        if ':' in expr:
            return [self.eval(x) for x in expr.split(':')]
        if expr[0].isdigit():
            if expr.endswith('h'):
                expr = '0x'+expr[:-1]
        return eval(expr, globals(), self)

    def value(self, str): return self.eval(str)

    def addr(self, addr):
        addr = self.eval(addr)
        if not isinstance(addr, (tuple, list)):
            raise Exception("Unknown address: " + str(addr))
        return addr

    def linear(self, addr):
        addr = self.eval(addr)
        if isinstance(addr, (int, long)):
            return addr
        addr = self.addr(addr)
        return (addr[0] << 4) + addr[1]
