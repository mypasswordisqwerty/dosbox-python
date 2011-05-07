#include <Python.h>
#include "string.h"
#include "vga.h"
#include "debug_api.h"

list<t_pyscript> scripts;
t_pyscript *current_script = NULL;

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
python_loadscripts(const char *sdir)
{
    int i;
    bool is_dir;
    DEBUG_ShowMsg("Loading python scripts from %s", sdir);
    dir_information * dir;
    dir = open_directory(sdir);
    if(!dir) return 0;

		python_init();

    char filename[CROSS_LEN];
    bool testRead = read_directory_first(dir, filename, is_dir);
    for ( ; testRead; testRead = read_directory_next(dir, filename, is_dir) ) {
			int len = strlen(filename);
			if(len > 3 && strcmp(&filename[len-3], ".py") == 0) {
				t_pyscript script = {0};	// init callback pointers to null
				snprintf(script.filename, CROSS_LEN, "%s/%s", sdir, filename);

				script.interpreter = Py_NewInterpreter();
				current_script = &script;
				initdosboxdbg();

				int ret = PyRun_SimpleFileEx(fopen(script.filename, "r"), script.filename, true);
				//PyObject* pyFile = PyFile_FromString(fullpath, "r");
				//int ret = PyRun_SimpleFile(PyFile_AsFile(pyFile), fullpath);
				//Py_DECREF(pyFile);

				if (ret == 0) {
					DEBUG_ShowMsg("Loaded %s\n", filename);
				} else {
					if(PyErr_Occurred() != NULL) {
						PyerrorHandler();
					}
					Py_EndInterpreter(script.interpreter);
					DEBUG_ShowMsg("Failed to load %s, ret=%i\n", filename, ret);
					continue;
				}

				scripts.push_back(script);
			}
    }
    close_directory(dir);
    return 0;
}

void
python_init()
{
	if (!Py_IsInitialized()) {
		Py_Initialize();
	} else {
		python_event(DBG_CLEANUP);
/*
		PyGILState_STATE state = PyGILState_Ensure();
		Py_AddPendingCall(&python_interrupt, NULL);
		PyGILState_Release(state);
		for (list<t_pyscript>::const_iterator it = scripts.begin(); it != scripts.end(); ++it) {
			PyThreadState_Swap((*it).interpreter);
			PyThreadState *state = PyThreadState_Get();
			Py_EndInterpreter((*it).interpreter);
		}
*/
	}
}

void
python_shutdown()
{
	if (Py_IsInitialized()) {
		python_event(DBG_CLEANUP);
		Py_Finalize();
	}
}


map<PyVoidCb,void*> *get_callbackmap(int evt)
{
	map<PyVoidCb,void*> *cbs;
	// todo: vector map?
	switch(evt) {
	case DBG_CLEANUP: cbs = &current_script->cleanup_cbs; break;
	case DBG_TICK: cbs = &current_script->tick_cbs; break;
	case DBG_VSYNC: cbs = &current_script->vsync_cbs; break;
	case DBG_BREAK: cbs = &current_script->break_cbs; break;
	default: return NULL;
	}
	return cbs;
}

void
python_event(int evt)
{
	for (list<t_pyscript>::iterator itr = scripts.begin(); itr != scripts.end(); ++itr) {
		PyThreadState_Swap((*itr).interpreter);
		current_script = &(*itr);

		map<PyVoidCb,void*> cbs = *get_callbackmap(evt);
		map<PyVoidCb,void*>::const_iterator end = cbs.end();
		//if(evt == DBG_VSYNC && cbs.size() > 0) DEBUG_ShowMsg("%i for %s", cbs.size(), current_script->filename);
		for (map<PyVoidCb,void*>::const_iterator it = cbs.begin(); it != end; ++it)
			it->first(it->second);

		if(evt == DBG_CLEANUP) {
			current_script->cleanup_cbs.clear();
			current_script->tick_cbs.clear();
			current_script->vsync_cbs.clear();
			current_script->break_cbs.clear();
		}
	}
}

void
python_log(int tick, const char *logger, char *msg)
{
	for (list<t_pyscript>::iterator itr = scripts.begin(); itr != scripts.end(); ++itr) {
		PyThreadState_Swap((*itr).interpreter);
		current_script = &(*itr);
		map<PyLogCbWrapper,void*>::const_iterator end = current_script->log_cbs.end();
		for (map<PyLogCbWrapper,void*>::const_iterator it = current_script->log_cbs.begin(); it != end; ++it)
			it->first(tick, logger, msg, it->second);
	}
}

void
python_register_break_cb(PyBreakCbWrapper cb, void *p)
{
	current_script->break_cbs[cb] = p;
}

void
python_unregister_break_cb(PyBreakCbWrapper cb, void *p)
{
	current_script->break_cbs.erase(cb);
}

void
python_register_event_cb(int evt, PyVoidCb cb, void *p)
{
	map<PyVoidCb,void*> *cbs = get_callbackmap(evt);
	(*cbs)[cb] = p;
}

void
python_unregister_event_cb(int evt, PyVoidCb cb, void *p)
{
	map<PyVoidCb,void*> *cbs = get_callbackmap(evt);
	cbs->erase(cb);
}

void
python_register_log_cb(PyLogCbWrapper cb, void *p)
{
	current_script->log_cbs[cb] = p;
}

void
python_unregister_log_cb(PyLogCbWrapper cb, void *p)
{
	current_script->log_cbs.erase(cb);
}

void
python_register_exec_cb(PyUIntWrap wrap, void *cb)
{
	current_script->exec_cb = cb;
}

PyObject*
python_registers()
{
	return Py_BuildValue("IIIIIIIII", reg_eax,reg_ebx,reg_ecx,reg_edx,
		reg_esi, reg_edi, reg_esp,reg_ebp,reg_eip);
}

PyObject*
python_segments()
{
	return Py_BuildValue("IIIIII", SegValue(cs), SegValue(ds),
		SegValue(es), SegValue(fs), SegValue(gs), SegValue(ss));
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
python_getmemory(Bitu loc, Bit32u num, std::string *mem)
{
	mem->reserve(num);
	for (Bitu x = 0; x < num; x++) {
		Bit8u val;
		if (mem_readb_checked(loc+x,&val)) val=0;
		mem->push_back(val);
	}
	return;
}

void
python_setmemory(Bitu loc, std::string *mem)
{
	char buf[mem->length()];
	mem->copy(buf, mem->length());
	for (Bitu x = 0; x < mem->length(); x++) {
		mem_writeb_checked(loc+x, buf[x]);
	}
	return;
}

void
python_getvidmemory(Bit16u x, Bit16u y, Bit16u w, Bit16u h, Bit8u page, std::string *mem)
{
	mem->reserve( w*h );
	for (Bitu i = 0; i < w*h; i++) {
		Bit8u val;
		INT10_GetPixel(x+(i%w), y+(i/w), page, &val);
		//Bit8u val = mem_readb(PhysMake(0xa000,i));
		mem->push_back(val);
	}
}

void
python_setvidmemory(Bit16u x, Bit16u y, Bit16u w, Bit16u h, Bit8u page, std::string *mem)
{
	char buf[mem->length()];
	mem->copy(buf, mem->length());
	for (Bitu i = 0; i < w*h; i++) {
		INT10_PutPixel(x+(i%w), y+(i/w), page, buf[i]);
	}
}

void 
python_getpalette(std::string *pal)
{
	int count=255;
	pal->reserve(count*3);
	// copied from INT10_GetDACBlock which uses emulator memory
  IO_Write(VGAREG_DAC_READ_ADDRESS,(Bit8u)0);
  for (;count>0;count--) {
    pal->push_back(IO_Read(VGAREG_DAC_DATA));
    pal->push_back(IO_Read(VGAREG_DAC_DATA));
    pal->push_back(IO_Read(VGAREG_DAC_DATA));
  }
}

void 
python_setpalette(std::string *pal)
{
	char buf[pal->length()];
	pal->copy(buf, pal->length());

	int count=255, i=0;
  IO_Write(VGAREG_DAC_WRITE_ADDRESS,(Bit8u)0);
  for (;count>0;count--) {
  		//if ((real_readb(BIOSMEM_SEG,BIOSMEM_MODESET_CTL)&0x06)==0) {
      //Bit32u i=(( 77*red + 151*green + 28*blue ) + 0x80) >> 8;
      //Bit8u ic=(i>0x3f) ? 0x3f : ((Bit8u)(i & 0xff));
      IO_Write(VGAREG_DAC_DATA,buf[i++]);
      IO_Write(VGAREG_DAC_DATA,buf[i++]);
      IO_Write(VGAREG_DAC_DATA,buf[i++]);
  }
}

int python_vgamode() { return CurMode->mode; }

void python_run(char *file) {
	unsigned int hash = MurmurFile(file);
	for (list<t_pyscript>::iterator itr = scripts.begin(); itr != scripts.end(); ++itr) {
		PyThreadState_Swap((*itr).interpreter);
		current_script = &(*itr);
		if(current_script->exec_cb != NULL)
			python_ExecCb(hash, current_script->exec_cb);
	}
}

