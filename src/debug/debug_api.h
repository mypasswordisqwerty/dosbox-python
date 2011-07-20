#ifdef C_DEBUG_SCRIPTING
#ifndef DOSBOX_DEBUG_API_H
#define DOSBOX_DEBUG_API_H

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
void DEBUG_ShowMsg(char const* format,...);
Bitu DEBUG_EnableDebugger();
Bitu DasmI386(char* buffer, PhysPt pc, Bitu cur_ip, bool bit32);

// -- MurmurHash2A.cpp

unsigned int MurmurFile (const char * filename);

// -- pybinding.cpp

extern void python_EventCb(void *p);
extern void python_ExecCb(unsigned int hash, void *p);
extern bool python_CliCmdCb(const char *cmd, void *p);

// --- TODO: cleanup callback handling

enum DEBUGEVENT { DBG_CLEANUP, DBG_TICK, DBG_VSYNC, DBG_BREAK, DBG_RESUME, DBGCB_COUNT };

typedef bool (*PyBreakCbWrapper) (CBreakpoint *bp, void *data);

typedef void (*PyVoidCb) (void *data);

typedef void (*PyUIntWrap) (unsigned int uint, void *data);

typedef bool (*PyCChrWrap) (const char *str, void *data);

typedef bool (*PyLogCbWrapper) (int tick, const char *logger, char *msg, void *data);

map<PyVoidCb,void*> *get_callbackmap(int evt);

typedef struct t_pyscript {
	char filename[CROSS_LEN];
	PyThreadState *interpreter;
	map<PyVoidCb,void*> cleanup_cbs, tick_cbs, vsync_cbs, break_cbs;
	map<PyBreakCbWrapper,void*> breakpoint_cbs;
	map<PyLogCbWrapper,void*> log_cbs;
	void *exec_cb;
	void *clicmd_cb;
} t_pyscript;

// -- pyscripting.cpp

void python_init();
std::string python_getscriptdir();
int python_loadscripts(std::string path);
void python_shutdown();
void python_event(int evt);
bool python_break(CBreakpoint *bp);
bool python_log(int tick, const char *logger, char *msg);
void python_run(char *file);
bool python_clicmd(char *cmd);

void python_register_break_cb(PyBreakCbWrapper cb, void *data);
void python_unregister_break_cb(PyBreakCbWrapper cb, void *data);
void python_register_event_cb(int evt, PyVoidCb cb, void *p);
void python_unregister_event_cb(int evt, PyVoidCb cb, void *p);

void python_register_clicmd_cb(PyCChrWrap wrap, void *cb);
void python_register_exec_cb(PyUIntWrap cb, void *p);
void python_unregister_exec_cb(PyUIntWrap cb, void *p);
void python_register_log_cb(PyLogCbWrapper cb, void *p);
void python_unregister_log_cb(PyLogCbWrapper cb, void *p);

PyObject* python_registers();
PyObject* python_segments();
std::list<CBreakpoint> python_bpoints();
char* python_dasm(Bit16u seg, Bit32u ofs, Bitu eip);
PyObject* python_mcbs();
void python_getmemory(Bitu loc, Bit32u num, std::string *mem);
void python_setmemory(Bitu loc, std::string *mem);
void python_getvidmemory(Bit16u x, Bit16u y, Bit16u w, Bit16u h, Bit8u page, std::string *mem);
void python_setvidmemory(Bit16u x, Bit16u y, Bit16u w, Bit16u h, Bit8u page, std::string *mem);
void python_getpalette(std::string *pal);
void python_setpalette(std::string *pal);
int python_vgamode();
std::list<CDebugVar> python_vars();
void python_insertvar(char *name, Bit32u addr);

PyMODINIT_FUNC initdosboxdbg(void);

#endif
#endif
