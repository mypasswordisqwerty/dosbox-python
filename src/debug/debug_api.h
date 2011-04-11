#ifndef DOSBOX_DEBUG_API_H
#define DOSBOX_DEBUG_API_H

#include <Python.h>
#include <list>
#include <map>
#include <string>
#include "config.h"
#include "cpu.h"
#include "paging.h"
#include "debug.hpp"

using namespace std;

// -- debug.cpp

bool ParseCommand(char* str);
void DEBUG_ShowMsg(char const* format,...);
Bitu DEBUG_EnableDebugger();
Bitu DasmI386(char* buffer, PhysPt pc, Bitu cur_ip, bool bit32);

// ---

typedef void (*PyTickCbWrapper) (void *data);
static map<PyTickCbWrapper,void*> tick_cbs;

typedef void (*PyLogCbWrapper) (int tick, const char *logger, char *msg, void *data);
static map<PyLogCbWrapper,void*> log_cbs;

// -- pyscripting.cpp

int python_init(const char *sdir);
void python_shutdown();
void python_ticks();
void python_log(int tick, const char *logger, char *msg);
void python_register_tick_cb(PyTickCbWrapper cb, void *data);
void python_unregister_tick_cb(PyTickCbWrapper cb, void *data);
void python_register_log_cb(PyLogCbWrapper cb, void *p);
void python_unregister_log_cb(PyLogCbWrapper cb, void *p);
PyObject* python_registers();
std::list<CBreakpoint> python_bpoints();
char* python_dasm(Bit16u seg, Bit32u ofs, Bitu eip);
void python_memory(Bitu seg, Bitu ofs1, Bit32u num, std::string *mem);

PyMODINIT_FUNC initdosboxdbg(void);

#endif
