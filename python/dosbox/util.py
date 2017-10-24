import binascii
import struct

_VARS = {}
REGS = ["eax", "ecx", "edx", "ebx", "esp", "ebp", "esi", "edi", "eip", "eflags", "cs", "ss", "ds", "es", "fs", "gs"]
WREGS = ["ax", "cx", "dx", "bx", "sp", "bp", "si", "di", "ip", "flags"]
BREGS = ["ah", "al", "ch", "cl", "dh", "dl", "bh", "bl"]
_FMTS = [None, '>B', '>H', None, '>I', None, None, None, '>Q']


def setRegs(regs):
    for i in range(len(regs)):
        _VARS[REGS[i]] = regs[i]


def setvar(name, val):
    _VARS[name] = val


def setvars(hash):
    _VARS.update(hash)


def var(name):
    if name in _VARS:
        return _VARS[name]
    if name in WREGS:
        return _VARS['e' + name] & 0xFFFF
    if name in BREGS:
        v = _VARS['e' + name[0] + 'x']
        return v & 0xFF if name[1] == 'l' else (v >> 8) & 0xFF
    v = binascii.unhexlify(name)
    print name, len(v), _FMTS[len(v)]
    return struct.unpack(_FMTS[len(v)], v)[0]


def tolinear(addr, seg=None):
    if isinstance(addr, basestring):
        if ':' in addr:
            a = addr.split(':')
            addr = [var(a[1]), var(a[0])]
        else:
            addr = var(addr)
    if isinstance(addr, (int, long)):
        return addr
    if not isinstance(addr, (tuple, list)):
        raise Exception("Unknown address: " + str(addr))
    if seg:
        addr = [addr, seg]
    return addr[0] + (addr[1] << 4)
