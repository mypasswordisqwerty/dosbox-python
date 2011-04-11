# 
# Example of Dosbox debugger python bindings
# (c)2011 <samuli.tuomola@gmail.com>
#
# Place this file in ~/.dosbox/python/
#

from dosboxdbg import *
import time

def hexdump(src, length=16):
    result=[]
    for i in xrange(0, len(src), length):
       s = src[i:i+length]
       hexa = b' '.join(["%02X"%ord(x) for x in s])
       text = b''.join([x if 0x20 <= ord(x) < 0x7F else b'.'  for x in s])
       result.append("%04X   %-*s   %s\n" % (i, length*3, hexa, text))
    return ''.join(result)

def tick():
	ShowMsg('tick %s' % time.ctime())
	UnregisterTick(tick)

def log(tick, logger, msg):
	if tick == 3 and logger == 'EXEC':
		ShowMsg('=== AT %i GOT "%s", will demo' % (tick,msg))
		demo()

def demo():
	regs = (eax,ebx,ecx,edx, esi,edi, esp,ebp,eip) = GetRegs()
	ShowMsg( 'registers: '+str(regs) )
	ShowMsg( 'executing: '+disasm(0xF000, eip, eip) )
	m = ReadMem(0xC843, 0x061E, 12)
	ShowMsg( 'some mem: '+hexdump(m) )
	EnableDebugger()
	ParseCommand("BP ")
	for h in GetBpoints():
		ShowMsg('BP %i. %x:%x' % (h.GetIntNr(), h.GetSegment(), h.GetOffset()))
		#ShowMsg(str(dir(h)))

ShowMsg("HELLO WORLD")
RegisterTick(tick)
RegisterLog(log)

