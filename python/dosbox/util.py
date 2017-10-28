
import dosbox
import binascii
import struct
from context import Context
try:
    from hexdump import hexdump as HD
except:
    HD = None


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


def hexdump(data):
    if HD:
        HD(data)
        return
    binascii.b2a_hex(data)


def readEnv(psp, progName=False):
    d = dosbox.Dosbox()
    ret = {}
    envs = struct.unpack('<H', d.mem((psp << 4)+0x2C, 2))[0]
    if envs == 0:
        return None
    mcb = struct.unpack('<BHH', d.mem((envs-1) << 4, 5))
    env = d.mem(envs << 4, mcb[2]*16)
    last = 0
    for x in env.split('\x00'):
        if last == 2:
            if progName:
                return x
            ret['programName'] = x
            break
        if last > 0:
            last += 1
            continue
        if len(x) == 0:
            last = 1
            continue
        if not progName:
            s = x.split('=')
            ret[s[0]] = s[1]
    return ret


def loadedProgs():
    psps = [0, 8]
    ret = {}
    d = dosbox.Dosbox()
    mcb = d.firstMCB()
    i = 0
    while True:
        m = struct.unpack('<BHH', d.mem(mcb << 4, 5))
        if m[1] not in psps:
            psps += [m[1]]
            ret[m[1]] = readEnv(m[1], True)
        if m[0] == 0x5A:
            break
        i += 1
        mcb += m[2]+1
    return ret
