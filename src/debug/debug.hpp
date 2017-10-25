#ifndef DOSBOX_DEBUG_HPP
#define DOSBOX_DEBUG_HPP
Bit32u GetAddress(Bit16u seg, Bit32u offset);

#include "dosbox.h"
#include "mem.h"
#include "support.h"
#include "cpu.h"
#include "paging.h"
#include <list>

#define BPINT_ALL 0x100


extern Bitu ignoreAddressOnce;

enum EBreakpoint { BKPNT_UNKNOWN, BKPNT_PHYSICAL, BKPNT_INTERRUPT, BKPNT_MEMORY, BKPNT_MEMORY_PROT, BKPNT_MEMORY_LINEAR, BKPNT_EXEC};

class CBreakpoint
{
public:

	CBreakpoint(void);
	void SetAddress(Bit16u seg, Bit32u off)	{ location = GetAddress(seg,off); type = BKPNT_PHYSICAL; segment = seg; offset = off; };
	void SetAddress(PhysPt adr) { location = adr; type = BKPNT_PHYSICAL; };
	void SetInt(Bit8u _intNr, Bit16u ah) { intNr = _intNr, ahValue = ah; type = BKPNT_INTERRUPT; };
	void SetOnce(bool _once) { once = _once; };
	void SetType(EBreakpoint _type) { type = _type; };
	void SetValue(Bit16u value) { ahValue = value; };
    void Run();

	bool IsActive(void) { return active; };
	void Activate(bool _active);

	EBreakpoint GetType(void) { return type; };
	bool GetOnce(void) { return once; };
	PhysPt GetLocation(void) { if (GetType()!=BKPNT_INTERRUPT)	return location;	else return 0; };
	Bit16u GetSegment(void) { return segment; };
	Bit32u GetOffset(void) { return offset; };
	Bit8u GetIntNr(void) { if (GetType()==BKPNT_INTERRUPT)	return intNr;		else return 0; };
	Bit16u GetValue(void) { if (GetType()!=BKPNT_PHYSICAL)	return ahValue;		else return 0; };
    unsigned int GetId(void) { return gid; }

	// statics
	static CBreakpoint* AddBreakpoint(Bit16u seg, Bit32u off, bool once);
	static CBreakpoint* AddIntBreakpoint(Bit8u intNum, Bit16u ah, bool once);
	static CBreakpoint* AddMemBreakpoint(Bit16u seg, Bit32u off);
    static CBreakpoint* AddExecBreakpoint(bool once);
	static void ActivateBreakpoints(PhysPt adr, bool activate);
	static bool CheckBreakpoint(PhysPt adr);
	static bool CheckBreakpoint(Bitu seg, Bitu off);
	static bool CheckIntBreakpoint(PhysPt adr, Bit8u intNr, Bit16u ahValue);
    static bool CheckExecBreakpoint(Bit16u seg, Bit32u off);
	static bool IsBreakpoint(PhysPt where);
	static bool IsBreakpointDrawn(PhysPt where);
	static bool DeleteBreakpoint(PhysPt where);
	static bool DeleteByIndex(Bit16u index);
	static void DeleteAll(void);
	static void ShowList(void);


private:
	EBreakpoint	type;
	// Physical
	PhysPt location;
	Bit8u oldData;
	Bit16u segment;
	Bit32u offset;
	// Int
	Bit8u intNr;
	Bit16u ahValue;
	// Shared
	bool active;
	bool once;
    unsigned int gid;

public:
	static std::list<CBreakpoint*> BPoints;
	static CBreakpoint* ignoreOnce;
    static unsigned int nextGlobalId;
};

/********************/
/* DebugVar   stuff */
/********************/

class CDebugVar
{
public:
	CDebugVar() {};
	CDebugVar(char* _name, PhysPt _adr) { adr=_adr; safe_strncpy(name,_name,16); };
	
	char*	GetName(void) { return name; };
	PhysPt	GetAdr (void) { return adr;  };

private:
	PhysPt  adr;
	char	name[16];

public: 
	static void			InsertVariable	(char* name, PhysPt adr);
	static CDebugVar*	FindVar			(PhysPt adr);
	static void			DeleteAll		();
	static bool			SaveVars		(char* name);
	static bool			LoadVars		(char* name);

	static std::list<CDebugVar*>	varList;
};

#endif
