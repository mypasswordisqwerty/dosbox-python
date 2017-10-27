//
//  breakpoint.cpp
//  dosbox
//
//  Created by john on 25.10.17.
//  Copyright © 2017 bjfn. All rights reserved.
//

#include "dosbox.h"
#if C_DEBUG
#include "debug.hpp"
#include "debug_api.h"

// Statics
std::list<CBreakpoint*> CBreakpoint::BPoints;
CBreakpoint*            CBreakpoint::ignoreOnce = 0;
Bitu                    ignoreAddressOnce = 0;
unsigned int            CBreakpoint::nextGlobalId = 0;

CBreakpoint::CBreakpoint(void):
location(0),
active(false),once(false),
segment(0),offset(0),intNr(0),ahValue(0),
type(BKPNT_UNKNOWN), gid(nextGlobalId++) { };

void CBreakpoint::Activate(bool _active)
{
#if !C_HEAVY_DEBUG
    if (GetType()==BKPNT_PHYSICAL) {
        if (_active) {
            // Set 0xCC and save old value
            Bit8u data = mem_readb(location);
            if (data!=0xCC) {
                oldData = data;
                mem_writeb(location,0xCC);
            };
        } else {
            // Remove 0xCC and set old value
            if (mem_readb (location)==0xCC) {
                mem_writeb(location,oldData);
            };
        }
    }
#endif
    active = _active;
};


CBreakpoint* CBreakpoint::AddBreakpoint(Bit16u seg, Bit32u off, bool once)
{
    CBreakpoint* bp = new CBreakpoint();
    bp->SetAddress        (seg,off);
    bp->SetOnce            (once);
    BPoints.push_front    (bp);
    return bp;
};

CBreakpoint* CBreakpoint::AddIntBreakpoint(Bit8u intNum, Bit16u ah, bool once)
{
    CBreakpoint* bp = new CBreakpoint();
    bp->SetInt            (intNum,ah);
    bp->SetOnce            (once);
    BPoints.push_front    (bp);
    return bp;
};

CBreakpoint* CBreakpoint::AddMemBreakpoint(Bit16u seg, Bit32u off)
{
    CBreakpoint* bp = new CBreakpoint();
    bp->SetAddress        (seg,off);
    bp->SetOnce            (false);
    bp->SetType            (BKPNT_MEMORY);
    BPoints.push_front    (bp);
    return bp;
};

CBreakpoint* CBreakpoint::AddExecBreakpoint(bool once)
{
    CBreakpoint* bp = new CBreakpoint();
    bp->SetOnce            (once);
    bp->SetType            (BKPNT_EXEC);
    BPoints.push_front    (bp);
    return bp;
};

void CBreakpoint::Run(){
#ifdef C_DEBUG_SCRIPTING
    PYTHON_Break(this);
#endif
}

void CBreakpoint::ActivateBreakpoints(PhysPt adr, bool activate)
{
    // activate all breakpoints
    std::list<CBreakpoint*>::iterator i;
    CBreakpoint* bp;
    for(i=BPoints.begin(); i != BPoints.end(); i++) {
        bp = (*i);
        // Do not activate, when bp is an actual address
        if (activate && (bp->GetType()==BKPNT_PHYSICAL) && (bp->GetLocation()==adr)) {
            // Do not activate :)
            continue;
        }
        bp->Activate(activate);
    };
};

bool CBreakpoint::CheckBreakpoint(Bitu seg, Bitu off)
// Checks if breakpoint is valid and should stop execution
{
    if ((ignoreAddressOnce!=0) && (GetAddress(seg,off)==ignoreAddressOnce)) {
        ignoreAddressOnce = 0;
        return false;
    } else
        ignoreAddressOnce = 0;

    // Search matching breakpoint
    std::list<CBreakpoint*>::iterator i;
    CBreakpoint* bp;
    for(i=BPoints.begin(); i != BPoints.end(); i++) {
        bp = (*i);
        if ((bp->GetType()==BKPNT_PHYSICAL) && bp->IsActive() && (bp->GetSegment()==seg) && (bp->GetOffset()==off)) {
            // Ignore Once ?
            if (ignoreOnce==bp) {
                ignoreOnce=0;
                bp->Activate(true);
                return false;
            };
            // Found,
            bp->Run();
            if (bp->GetOnce()) {
                // delete it, if it should only be used once
                (BPoints.erase)(i);
                bp->Activate(false);
                delete bp;
            } else {
                ignoreOnce = bp;
            };
            return true;
        }
#if C_HEAVY_DEBUG
        // Memory breakpoint support
        else if (bp->IsActive()) {
            if ((bp->GetType()==BKPNT_MEMORY) || (bp->GetType()==BKPNT_MEMORY_PROT) || (bp->GetType()==BKPNT_MEMORY_LINEAR)) {
                // Watch Protected Mode Memoryonly in pmode
                if (bp->GetType()==BKPNT_MEMORY_PROT) {
                    // Check if pmode is active
                    if (!cpu.pmode) return false;
                    // Check if descriptor is valid
                    Descriptor desc;
                    if (!cpu.gdt.GetDescriptor(bp->GetSegment(),desc)) return false;
                    if (desc.GetLimit()==0) return false;
                }

                Bitu address;
                if (bp->GetType()==BKPNT_MEMORY_LINEAR) address = bp->GetOffset();
                else address = GetAddress(bp->GetSegment(),bp->GetOffset());
                Bit8u value=0;
                if (mem_readb_checked(address,&value)) return false;
                if (bp->GetValue() != value) {
                    // Yup, memory value changed
                    DEBUG_ShowMsg("DEBUG: Memory breakpoint %s: %04X:%04X - %02X -> %02X\n",(bp->GetType()==BKPNT_MEMORY_PROT)?"(Prot)":"",bp->GetSegment(),bp->GetOffset(),bp->GetValue(),value);
                    bp->SetValue(value);
                    bp->Run();
                    return true;
                };
            }
        };
#endif
    };
    return false;
};

bool CBreakpoint::CheckIntBreakpoint(PhysPt adr, Bit8u intNr, Bit16u ahValue)
// Checks if interrupt breakpoint is valid and should stop execution
{
    if ((ignoreAddressOnce!=0) && (adr==ignoreAddressOnce)) {
        ignoreAddressOnce = 0;
        return false;
    } else
        ignoreAddressOnce = 0;

    // Search matching breakpoint
    std::list<CBreakpoint*>::iterator i;
    CBreakpoint* bp;
    for(i=BPoints.begin(); i != BPoints.end(); i++) {
        bp = (*i);
        if ((bp->GetType()==BKPNT_INTERRUPT) && bp->IsActive() && (bp->GetIntNr()==intNr)) {
            if ((bp->GetValue()==BPINT_ALL) || (bp->GetValue()==ahValue)) {
                // Ignore it once ?
                if (ignoreOnce==bp) {
                    ignoreOnce=0;
                    bp->Activate(true);
                    return false;
                };
                // Found
                bp->Run();
                if (bp->GetOnce()) {
                    // delete it, if it should only be used once
                    (BPoints.erase)(i);
                    bp->Activate(false);
                    delete bp;
                } else {
                    ignoreOnce = bp;
                }
                return true;
            }
        };
    };
    return false;
};

bool CBreakpoint::CheckExecBreakpoint(Bit16u seg, Bit32u off, Bit16u pspseg) {
    std::list<CBreakpoint*>::iterator i;
    CBreakpoint* bp;
    for(i=BPoints.begin(); i != BPoints.end(); i++) {
        bp = (*i);
        if ((bp->GetType()==BKPNT_EXEC)) {
                // Found
                bp->segment = seg;
                bp->offset = off;
                bp->ahValue = pspseg;
                bp->Run();
                if (bp->GetOnce()) {
                    // delete it, if it should only be used once
                    (BPoints.erase)(i);
                    bp->Activate(false);
                    delete bp;
                } else {
                    ignoreOnce = bp;
                }
                return true;
            }
        };
    return false;
}

void CBreakpoint::DeleteAll()
{
    std::list<CBreakpoint*>::iterator i;
    CBreakpoint* bp;
    for(i=BPoints.begin(); i != BPoints.end(); i++) {
        bp = (*i);
        bp->Activate(false);
        delete bp;
    };
    (BPoints.clear)();
};


bool CBreakpoint::DeleteByIndex(Bit16u index)
{
    // Search matching breakpoint
    int nr = 0;
    std::list<CBreakpoint*>::iterator i;
    CBreakpoint* bp;
    for(i=BPoints.begin(); i != BPoints.end(); i++) {
        if (nr==index) {
            bp = (*i);
            (BPoints.erase)(i);
            bp->Activate(false);
            delete bp;
            return true;
        }
        nr++;
    };
    return false;
};

bool CBreakpoint::DeleteBreakpoint(PhysPt where)
{
    // Search matching breakpoint
    std::list<CBreakpoint*>::iterator i;
    CBreakpoint* bp;
    for(i=BPoints.begin(); i != BPoints.end(); i++) {
        bp = (*i);
        if ((bp->GetType()==BKPNT_PHYSICAL) && (bp->GetLocation()==where)) {
            (BPoints.erase)(i);
            bp->Activate(false);
            delete bp;
            return true;
        }
    };
    return false;
};

bool CBreakpoint::IsBreakpoint(PhysPt adr)
// is there a breakpoint at address ?
{
    // Search matching breakpoint
    std::list<CBreakpoint*>::iterator i;
    CBreakpoint* bp;
    for(i=BPoints.begin(); i != BPoints.end(); i++) {
        bp = (*i);
        if ((bp->GetType()==BKPNT_PHYSICAL) && (bp->GetSegment()==adr)) {
            return true;
        };
        if ((bp->GetType()==BKPNT_PHYSICAL) && (bp->GetLocation()==adr)) {
            return true;
        };
    };
    return false;
};

bool CBreakpoint::IsBreakpointDrawn(PhysPt adr)
// valid breakpoint, that should be drawn ?
{
    // Search matching breakpoint
    std::list<CBreakpoint*>::iterator i;
    CBreakpoint* bp;
    for(i=BPoints.begin(); i != BPoints.end(); i++) {
        bp = (*i);
        if ((bp->GetType()==BKPNT_PHYSICAL) && (bp->GetLocation()==adr)) {
            // Only draw, if breakpoint is not only once,
            return !bp->GetOnce();
        };
    };
    return false;
};

void CBreakpoint::ShowList(void)
{
    // iterate list
    int nr = 0;
    std::list<CBreakpoint*>::iterator i;
    for(i=BPoints.begin(); i != BPoints.end(); i++) {
        CBreakpoint* bp = (*i);
        if (bp->GetType()==BKPNT_PHYSICAL) {
            DEBUG_ShowMsg("%02X. BP %04X:%04X\n",nr,bp->GetSegment(),bp->GetOffset());
        } else if (bp->GetType()==BKPNT_INTERRUPT) {
            if (bp->GetValue()==BPINT_ALL)    DEBUG_ShowMsg("%02X. BPINT %02X\n",nr,bp->GetIntNr());
            else                            DEBUG_ShowMsg("%02X. BPINT %02X AH=%02X\n",nr,bp->GetIntNr(),bp->GetValue());
        } else if (bp->GetType()==BKPNT_MEMORY) {
            DEBUG_ShowMsg("%02X. BPMEM %04X:%04X (%02X)\n",nr,bp->GetSegment(),bp->GetOffset(),bp->GetValue());
        } else if (bp->GetType()==BKPNT_MEMORY_PROT) {
            DEBUG_ShowMsg("%02X. BPPM %04X:%08X (%02X)\n",nr,bp->GetSegment(),bp->GetOffset(),bp->GetValue());
        } else if (bp->GetType()==BKPNT_MEMORY_LINEAR ) {
            DEBUG_ShowMsg("%02X. BPLM %08X (%02X)\n",nr,bp->GetOffset(),bp->GetValue());
        };
        nr++;
    }
};

#endif
