"""
 cheat.py - Memory scanner and cheat management script for Dosbox
 (c)2011, <samuli@tuomola.net>
"""
from dosboxdbg import *
import re, struct, binascii
import sqlite3

locs = []
token = ''
runhash = None
holds = {}

def HELP(p):
	ShowMsg("cheat.py commands:")
	ShowMsg('-' * 74)
	for c in sorted(cmds):
		if cmds[c].__doc__ != None:
			ShowMsg("%s\t%s" % (c, cmds[c].__doc__))
	ShowMsg('')

def findall(needle, haystack):
	return [m.start() for m in re.finditer(re.escape(needle), haystack)]

#return ''.join( [ "%02X " % ord(x) for x in bytes ] ).strip()
def hex2bin(h):
	if h.upper().startswith('0X') or ' ' in h:
		h = h.upper().replace('0X','').replace(' ','')
	return binascii.unhexlify(h)
	#return [chr(int(h[i:i+2], 16)) for i in xrange(0, len(h), 2)]

def StrToAddr(s):
	return GetAddress(*[int(i,16) for i in s.split(':')])

def MSRCH(par):
	""" Search allocated memory for a value """
	global locs, token
	locs = []
	token = hex2bin(par)
	mcb = GetMCBs()
	ssz = 0
	ShowMsg(repr(mcb))
	for mseg in mcb:
		addr = GetAddress(mseg,0)
		mem = ReadMem(addr, mcb[mseg])
		locs += ['%x:%x'%(mseg,n) for n in findall(token, mem)]
		ssz += mcb[mseg]
	ShowMsg('found %s for %i times in %ib of memory' %(repr(token), len(locs), ssz))
	return True

def MFILT(par):
	""" Filter previously searched locations with a new value """
	global locs, token
	
	if par.upper() == 'INC':
		locs = [n for n in locs if ReadMem(StrToAddr(n), len(token)) > token]
	elif par.upper() == 'DEC':
		locs = [n for n in locs if ReadMem(StrToAddr(n), len(token)) < token]
	else:
		if ' ' in par and par[0].isalpha():
			# if "[a-z] [0-9]*" then assume a formatted value
			tok = struct.unpack(*par.split(' ',1))
		else:
			# otherwise simple hexvalue
			tok = hex2bin(par)
		if len(tok) != len(token):
			ShowMsg('search token length should match original search length: %i'%len(token))
			return False
		#locs = [n for n in locs if ReadMem(GetAddress(*map(int,n.split(':'))), len(tok)) == tok]
		locs = [n for n in locs if ReadMem(StrToAddr(n), len(tok)) == tok]

	ShowMsg('%i remaining' % len(locs))
	return True

def MLST(p):
	""" List previously searched/filtered values """
	global locs
	rep = repr(locs)
	for i,n in enumerate(locs):
		ShowMsg('%s %s' % (n, repr(ReadMem(StrToAddr(n), len(token)))))
	# split for ui output, todo: clean api
	#for i in xrange(0, len(rep), 253): ShowMsg(rep[i:i+253])
	return True

def MHOLD(par):
	""" Watch a memory location and prevent changes (16bit values atm) """
	for v in GetVars():
		if v.GetName().lower() == par.strip().lower():
			holds[v.GetAdr()] = ReadMem(v.GetAdr(),2)
			ShowMsg('holding '+par+repr(holds))
			ParseCommand('BPM 0:%x' % v.GetAdr())
			#for bp in GetBPs(): ShowMsg('%i %x' % (bp.GetLocation(), bp.GetOffset()))
			return True
	ShowMsg('no such var %s?' % par)
#		ShowMsg('%s %i' % (v.GetName(),v.GetAdr()))

def MSAVE(p):
	""" Save current set of variables """
	con = sqlitecon()
	c = con.cursor()
	sql = 'select id,name,(select count(*) from fields where gameid=id) as fc from games where hash=?'
	c.execute(sql, (hex(binhash),))
	res = c.fetchone()
	if len(res) > 0:
		gameid = res['id']
		if int(res['fc']) > 0:
			c.execute("delete from fields where gameid=?", gameid)
	else:
		c.execute("insert into games (id,name,hash) values(?,?,?)", (None,'',runhash))
		gameid = c.lastrowid
	#
	c.executemany("insert into fields (gameid,name,addr) values(?, ?, ?)",
		[(gameid, v.GetName(), v.GetAdr()) for v in GetVars()])
	con.commit()

def MV(par):
	""" Modify variable """
	var,val = par.rsplit(' ',1)
	val = hex2bin(val)
	#ShowMsg(':'.join([v.GetName() for v in GetVars()]))
	for v in GetVars():
		if v.GetName().lower() == var.lower():
			ShowMsg('Changed %s'%var)
			WriteMem(v.GetAdr(), val)
			return True
	ShowMsg('%s not found' % var)

def CLST(p):
	""" List available code changes for running binary """
	if runhash == None:
		raise Exception('Exec hash missing (script reloading unsupported atm)')
	con = sqlitecon()
	c = con.cursor()
	sql = 'select id,name,(select count(*) from codes where gameid=id) as cc from games where hash=?'
	c.execute(sql, (hex(runhash),))
	res = c.fetchone()
	if len(res) > 0:
		ShowMsg('%i code changes for %s' %(res['cc'], res['name']))
		c.execute('select name,offset,originst,newinst from codes where gameid=?', (res['id'],))
		res = c.fetchall()
		ret = True
		for c in res:
			oinst = hex2bin(c['originst'])
			ninst = hex2bin(c['newinst'])
			cod = ReadMem(GetAddress(0x191,c['offset']), len(oinst))
			if cod != oinst:
				ShowMsg("%s: %s doesn't match expected %s" % (c['name'], repr(cod), repr(oinst)))
				ret = False
			else:
				ShowMsg('%s: found at offset %i' % (c['name'], c['offset']))
		return ret
	#

def loadCode(name):
	c = sqlitecon().cursor()
	c.execute('select * from codes where gameid=(select id from games where hash=?) and name=?', (hex(runhash),name))
	return c.fetchone()

def CON(para):
	""" Alter the code / apply a cheat """
	if runhash == None: raise Exception('Reloading not currently supported')
	c = loadCode(para)
	if c == None:
		ShowMsg('%s not found'%para)
		return
	oinst = hex2bin(c['originst'])
	ninst = hex2bin(c['newinst'])
	cod = ReadMem(GetAddress(0x191,c['offset']), len(oinst))
	if cod != oinst:
		ShowMsg("%s: %s doesn't match expected %s" % (c['name'], repr(cod), repr(oinst)))
	else:
		WriteMem(GetAddress(0x191,c['offset']), ninst)
		ShowMsg('%s applied'%para)
		return True

def COFF(para):
	""" Reverse previous code change """
	if runhash == None: raise Exception('Reloading not currently supported')
	c = loadCode(para)
	if c == None:
		ShowMsg('%s not found'%para)
		return
	oinst = hex2bin(c['originst'])
	ninst = hex2bin(c['newinst'])
	cod = ReadMem(GetAddress(0x191,c['offset']), len(oinst))
	if cod != ninst:
		ShowMsg("%s: doesn't appear to be loaded, instead %s" % (c['name'], repr(cod)))
	else:
		WriteMem(GetAddress(0x191,c['offset']), oinst)
		return True


cmds = {
	'HELP':HELP, 'MV':MV,
	'MSRCH':MSRCH,'MFILT':MFILT,'MLST':MLST,'MHOLD':MHOLD,'MSAVE':MSAVE,
	'CLST':CLST, 'CON':CON, 'COFF':COFF
}

# --------- Callbacks..

def memChange(bp):
	if bp.GetLocation() in holds.keys():
		if ReadMem(bp.GetLocation(),2) == holds[bp.GetLocation()]: return False
		ShowMsg('memchang %i %s' % (bp.GetLocation(), repr(ReadMem(bp.GetLocation(),2))))
		ShowMsg('in hold %s'% repr(holds[bp.GetLocation()]))
		WriteMem(bp.GetLocation(), holds[bp.GetLocation()])
		ShowMsg('now %s'% repr(ReadMem(bp.GetLocation(),2)))
		return False

RegisterBreak(memChange)

def cmd(cmdline):
	global locs
	try:
		if ' ' not in cmdline: cmdline += ' '
		cmd,para = cmdline.split(' ',1)
		cmd = cmd.upper()
		if cmds.has_key(cmd):
			return cmds.get(cmd)(para)
	except Exception as e:
		import traceback
		ShowMsg(traceback.format_exc())
	return False

ListenForCmd(cmd)

def sqlitecon():
	global cheatCon
	try:
		return cheatCon
	except NameError:
		cheatCon = sqlite3.connect(GetScriptDir()+'/cheat.db')
		cheatCon.row_factory = sqlite3.Row
		ShowMsg('opened '+GetScriptDir()+'/cheat.db')
		return cheatCon

def executed(fn):
	global runhash
	binhash = PMurHash32_File(1, fn)
	if binhash == 0: return
	ShowMsg('Running: %s %X' % (fn, binhash))
	con = sqlitecon()
	c = con.cursor()
	sql = '''
		select id,g.name,count(f.name) as fc,count(c.name) as cc from games as g 
		left join fields as f on(f.gameid=id) left join codes as c on(c.gameid=id) 
		where hash=?
		'''
	# hex adds a suffix for longs for some reason
	hexhash = hex(binhash).replace('L','')
	c.execute(sql, (hexhash,))
	res = c.fetchone()
	
	if res['fc']>0 or res['cc']>0:
		runhash = binhash
		ShowMsg('%i fields and %i codes for %s' %(res['fc'], res['cc'], res['name']))
		ShowMsg('add %i' % GetAddress(0,100))
		c.execute('select name,rawaddr from fields where gameid=?', (res['id'],))
		res = c.fetchall()
		for c in res:
			ShowMsg('%s %x' % (c['name'], c['rawaddr']))
			InsertVar(c['name'], c['rawaddr'])

ListenForExec(executed)
