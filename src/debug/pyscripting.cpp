#include <Python.h>
#include "cross.h"
#include "string.h"
#include "debug_api.h"

char save_error_type[1024], save_error_info[1024];

void 
PyerrorHandler()
{
   PyObject *errobj, *errdata, *errtraceback, *pystring;
 
   PyErr_Fetch(&errobj, &errdata, &errtraceback);
 
   pystring = NULL;
   if (errobj != NULL &&
      (pystring = PyObject_Str(errobj)) != NULL &&     /* str(object) */
      (PyString_Check(pystring))
      )
       strcpy(save_error_type, PyString_AsString(pystring));
   else
       strcpy(save_error_type, "<unknown exception type>");
   Py_XDECREF(pystring);
 
   pystring = NULL;
   if (errdata != NULL &&
      (pystring = PyObject_Str(errdata)) != NULL &&
      (PyString_Check(pystring))
      )
       strcpy(save_error_info, PyString_AsString(pystring));
   else
       strcpy(save_error_info, "<unknown exception data>");
   Py_XDECREF(pystring);
 
   DEBUG_ShowMsg("%s\n%s\n", save_error_type, save_error_info);
   Py_XDECREF(errobj);
   Py_XDECREF(errdata);         /* caller owns all 3 */
   Py_XDECREF(errtraceback);    /* already NULL'd out */
}

int
python_init(const char *sdir)
{
    PyObject *pName, *pModule, *pDict, *pFunc;
    PyObject *pArgs, *pValue;
    int i;
    bool is_dir;

    DEBUG_ShowMsg("Loading python scripts from %s", sdir);
    Py_Initialize();
    initdosboxdbg();

    dir_information * dir;
    dir = open_directory(sdir);
    if(!dir) return 0;

    char filename[CROSS_LEN];
    bool testRead = read_directory_first(dir, filename, is_dir);
    for ( ; testRead; testRead = read_directory_next(dir, filename, is_dir) ) {
			int len = strlen(filename);
			if(len > 3 && strcmp(&filename[len-3], ".py") == 0) {
				char fullpath[CROSS_LEN];
				snprintf(fullpath, CROSS_LEN, "%s/%s", sdir, filename);
				pName = PyString_FromString(fullpath);
				Py_DECREF(pName);
				int ret = PyRun_SimpleFileEx(fopen(fullpath, "r"), fullpath, true);
				if (ret == 0) {
					DEBUG_ShowMsg("Finished %s\n", filename);
				} else {
					if(PyErr_Occurred() != NULL) {
						PyerrorHandler();
					}
					DEBUG_ShowMsg("Failed to load %s, ret=%i\n", filename, ret);
				}
			}
    }
    close_directory(dir);
    return 0;
}

void
python_shutdown()
{
    Py_Finalize();
}

void
python_ticks()
{
	map<PyTickCbWrapper,void*>::const_iterator end = tick_cbs.end();
	for (map<PyTickCbWrapper,void*>::const_iterator it = tick_cbs.begin(); it != end; ++it)
		it->first(it->second);
}

void
python_log(int tick, const char *logger, char *msg)
{
	map<PyLogCbWrapper,void*>::const_iterator end = log_cbs.end();
	for (map<PyLogCbWrapper,void*>::const_iterator it = log_cbs.begin(); it != end; ++it)
		it->first(tick, logger, msg, it->second);
}

void
python_register_tick_cb(PyTickCbWrapper cb, void *p)
{
	tick_cbs[cb] = p;
}

void
python_unregister_tick_cb(PyTickCbWrapper cb, void *p)
{
	tick_cbs.erase(cb);
}

void
python_register_log_cb(PyLogCbWrapper cb, void *p)
{
	log_cbs[cb] = p;
}

void
python_unregister_log_cb(PyLogCbWrapper cb, void *p)
{
	log_cbs.erase(cb);
}

PyObject*
python_registers()
{
	return Py_BuildValue("IIIIIIIII", reg_eax,reg_ebx,reg_ecx,reg_edx,
		reg_esi, reg_edi, reg_esp,reg_ebp,reg_eip);
}

std::list<CBreakpoint>
python_bpoints()
{
	std::list<CBreakpoint> ret;
	std::list<CBreakpoint*>::iterator i;
	for(i=CBreakpoint::BPoints.begin(); i != CBreakpoint::BPoints.end(); i++) {
		CBreakpoint *bp = (*i);
		ret.push_back(*bp);
	}
	return ret;
}

char dasmstr[200];
char*
python_dasm(Bit16u seg, Bit32u ofs, Bitu eip)
{
	PhysPt ptr = GetAddress(seg,ofs);
	Bitu size = DasmI386(dasmstr, ptr, eip, cpu.code.big);
	return dasmstr;
}

void
python_memory(Bitu seg, Bitu ofs1, Bit32u num, std::string *mem)
{
	mem->reserve(num);
	for (Bitu x = 0; x < num; x++) {
		Bit8u val;
		if (mem_readb_checked(GetAddress(seg,ofs1+x),&val)) val=0;
		mem->push_back(val);
	}
	return;
}

