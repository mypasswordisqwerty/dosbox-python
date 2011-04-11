#ifndef DOSBOX_DEBUG_HPP
#define DOSBOX_DEBUG_HPP
Bit32u GetAddress(Bit16u seg, Bit32u offset);


enum EBreakpoint { BKPNT_UNKNOWN, BKPNT_PHYSICAL, BKPNT_INTERRUPT, BKPNT_MEMORY, BKPNT_REGISTER, BKPNT_MEMORY_PROT, BKPNT_MEMORY_LINEAR };
enum ERegister { REG_UNKNOWN, REG_EAX, REG_EBX, REG_ECX, REG_EDX, REG_ESI, REG_EDI, REG_EBP, REG_ESP, REG_EIP };

class CBreakpoint
{
public:

	CBreakpoint(void);
	void					SetAddress		(Bit16u seg, Bit32u off)	{ location = GetAddress(seg,off);	type = BKPNT_PHYSICAL; segment = seg; offset = off; };
	void					SetAddress		(PhysPt adr)				{ location = adr;				type = BKPNT_PHYSICAL; };
	void					SetInt			(Bit8u _intNr, Bit16u ah)	{ intNr = _intNr, ahValue = ah; type = BKPNT_INTERRUPT; };
	void					SetOnce			(bool _once)				{ once = _once; };
	void					SetType			(EBreakpoint _type)			{ type = _type; };
	void					SetValue		(Bit16u value)				{ ahValue = value; };
	void					SetReg		(ERegister _reg)		{ reg = _reg; };

	bool					IsActive		(void)						{ return active; };
	void					Activate		(bool _active);

	EBreakpoint				GetType			(void)						{ return type; };
	bool					GetOnce			(void)						{ return once; };
	PhysPt					GetLocation		(void)						{ if (GetType()!=BKPNT_INTERRUPT)	return location;	else return 0; };
	Bit16u					GetSegment		(void)						{ return segment; };
	Bit32u					GetOffset		(void)						{ return offset; };
	Bit8u					GetIntNr		(void)						{ if (GetType()==BKPNT_INTERRUPT)	return intNr;		else return 0; };
	Bit16u					GetValue		(void)						{ if (GetType()!=BKPNT_PHYSICAL)	return ahValue;		else return 0; };
	ERegister				GetReg			(void)						{ return reg; };

	// statics
	static CBreakpoint*		AddBreakpoint		(Bit16u seg, Bit32u off, bool once);
	static CBreakpoint*		AddIntBreakpoint	(Bit8u intNum, Bit16u ah, bool once);
	static CBreakpoint*		AddMemBreakpoint	(Bit16u seg, Bit32u off);
	static CBreakpoint*		AddRegBreakpoint	(char *reg, Bit16u val);
	static void				ActivateBreakpoints	(PhysPt adr, bool activate);
	static bool				CheckBreakpoint		(PhysPt adr);
	static bool				CheckBreakpoint		(Bitu seg, Bitu off);
	static bool				CheckIntBreakpoint	(PhysPt adr, Bit8u intNr, Bit16u ahValue);
	static bool				IsBreakpoint		(PhysPt where);
	static bool				IsBreakpointDrawn	(PhysPt where);
	static bool				DeleteBreakpoint	(PhysPt where);
	static bool				DeleteByIndex		(Bit16u index);
	static void				DeleteAll			(void);
	static void				ShowList			(void);


private:
	EBreakpoint	type;
	ERegister reg;
	// Physical
	PhysPt		location;
	Bit8u		oldData;
	Bit16u		segment;
	Bit32u		offset;
	// Int
	Bit8u		intNr;
	Bit16u		ahValue;
	// Shared
	bool		active;
	bool		once;

public:
	static std::list<CBreakpoint*>	BPoints;
	static CBreakpoint*				ignoreOnce;
};

#endif
