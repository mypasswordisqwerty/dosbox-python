from dosboxdbg import *

def logged(tick, logger, mesg):
	" Some games like to reset stuff in loops, skip logging "
	# black thorne
	if logger == 'PIT' and '0 Timer at' in mesg:
		return False
	# warcraft 1
	if logger == 'SBLASTER' and 'Raising IRQ' in mesg:
		return False
	
ListenForLog(logged)
