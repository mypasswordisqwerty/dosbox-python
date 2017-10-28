#ifndef DOSBOX_DEBUG_API_H
#define DOSBOX_DEBUG_API_H

#ifdef C_DEBUG_SCRIPTING

#include <Python.h>
#include <list>
#include <map>
#include <string>
#include "config.h"
#include "cpu.h"
#include "cross.h"
#include "paging.h"
#include "inout.h"
#include "../ints/int10.h"
#include "dos_inc.h"
#include "debug.hpp"

using namespace std;

// -- debug.cpp

bool ParseCommand(char* str);
Bitu DEBUG_EnableDebugger();
Bitu DasmI386(char* buffer, PhysPt pc, Bitu cur_ip, bool bit32);
void DEBUG_Continue(void);
Bitu DEBUG_Next(void);
Bitu DEBUG_Step(void);
bool PYTHON_IsDosboxUI(void);
Bitu PYTHON_Loop(bool& dosboxUI);
bool PYTHON_Command(const char *cmd);
bool PYTHON_Break(CBreakpoint *bp);
char* PYTHON_Dasm(PhysPt ptr, Bitu eip, int &sz);
// -- pyscripting.cpp

void python_getvidmemory(Bit16u x, Bit16u y, Bit16u w, Bit16u h, Bit8u page, std::string *mem);
void python_setvidmemory(Bit16u x, Bit16u y, Bit16u w, Bit16u h, Bit8u page, std::string *mem);
void python_getpalette(std::string *pal);
void python_setpalette(std::string *pal);
int python_vgamode();
std::list<CDebugVar> python_vars();
void python_insertvar(char *name, Bit32u addr);

#endif
#endif
