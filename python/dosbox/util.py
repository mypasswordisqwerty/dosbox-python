
import dosbox
from context import Context


def readString(addr="ds:dx", end='\x00', maxsize=256):
    data = dosbox.Dosbox().mem(addr, maxsize)
    idx = data.find(end)
    if idx >= 0:
        data = data[:idx]
    return data


def parseFlags():
    f = Context().var('eflags')
    return {'CF': f & 1, 'PF': (f >> 2) & 1, 'AF': (f >> 4) & 1, 'ZF': (f >> 6) & 1, 'SF': (f >> 7) & 1,
            'TF': (f >> 8) & 1, 'IF': (f >> 9) & 1, 'DF': (f >> 10) & 1, 'OF': (f >> 11) & 1}


def isCarry():
    return (Context().var('eflags') & 1) != 0
