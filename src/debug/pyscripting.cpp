#include "dosbox.h"
#include <Python.h>
#include <string.h>
#include "vga.h"
#include "control.h"
#include "debug_api.h"
#include "setup.h"
#include "debug_inc.h"
#include <signal.h>
#include "bindings/_dbox.h"

bool dosboxUI = false;

int
python_loadscripts(std::string path)
{
    bool is_dir;
    const char *sdir = path.c_str();
    DEBUG_ShowMsg("Loading python scripts from %s", sdir);
    dir_information * dir;
    dir = open_directory(sdir);
    if(!dir) return 0;

    char filename[CROSS_LEN];
    bool testRead = read_directory_first(dir, filename, is_dir);
    for ( ; testRead; testRead = read_directory_next(dir, filename, is_dir) ) {
			size_t len = strlen(filename);
			if(len > 3 && strcmp(&filename[len-3], ".py") == 0) {
				//snprintf(script.filename, CROSS_LEN, "%s/%s", sdir, filename);
                //TODO: import scripts
            }
    }
    close_directory(dir);
    return 0;
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
char* PYTHON_Dasm(PhysPt ptr, Bitu eip, int &size)
{
	size = (int)DasmI386(dasmstr, ptr, eip, cpu.code.big);
	return dasmstr;
}


PyObject*
python_mcbs()
{
//	std::vector<int> addrs;
	PyObject *dict = PyDict_New();
	Bit16u mcb_segment = dos.firstMCB;
	DOS_MCB mcb(mcb_segment);
	char filename[9]; // basename=8+NUL
	while (true) {
		// verify that the type field is valid
		if (mcb.GetType()!=0x4d && mcb.GetType()!=0x5a) {
      LOG(LOG_MISC,LOG_ERROR)("MCB chain broken at %04X:0000!",mcb_segment);
		}

		mcb.GetFileName(filename);
		switch (mcb.GetPSPSeg()) {
			case MCB_FREE:
			case MCB_DOS:
				break;
			default:
                break;
				// get memory blocks reserved by the running binary
                /*
				if(strlen(filename) > 0 && strncasecmp(exec_filename, filename, strlen(filename)) == 0) {
					PyDict_SetItem(dict, Py_BuildValue("i",mcb_segment), 
							Py_BuildValue("i",mcb.GetSize() << 4));
				} else {
					DEBUG_ShowMsg("%s != %s", exec_filename, filename);
				}
                 */
		}
		
    // if we've just processed the last MCB in the chain, break out of the loop
    if (mcb.GetType()==0x5a) {
      break;
    }
    // else, move to the next MCB in the chain
    mcb_segment+=mcb.GetSize()+1;
    mcb.SetPt(mcb_segment);
  }
  
  return dict;
  //return Py_BuildValue("{i:i}", &addrs[0]
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

void
python_insertvar(char *name, Bit32u addr)
{
	CDebugVar::InsertVariable(name, addr);
}

std::list<CDebugVar>
python_vars()
{
	std::list<CDebugVar> ret;
	std::list<CDebugVar*>::iterator i;
	for(i=CDebugVar::varList.begin(); i != CDebugVar::varList.end(); i++) {
		CDebugVar *var = (*i);
		ret.push_back(*var);
	}
	return ret;
}

#include <libgen.h>
#include "../dos/drives.h"

extern DOS_File * Files[DOS_FILES];

void
python_run(char *file, Bit16u pspseg, Bit16u loadseg, Bit16u seg, Bit32u off)
{

    DEBUG_ShowMsg("EXEC: %s @%04X psp:%04X csip:%04X:%04X", file, loadseg, pspseg, seg, off);
    return;
    Bit8u drive;char fullname[DOS_PATHLENGTH];
    if (!DOS_MakeName(file, fullname, &drive) ||
            strncmp(Drives[drive]->GetInfo(),"local directory",15)) {
        return;
    }

    localDrive *drv = dynamic_cast<localDrive*>(Drives[drive]);
    if (drv == NULL) {
        DEBUG_ShowMsg("Drive not found");
        return;
    }

    char sysname[CROSS_LEN];
    drv->GetSystemFilename(sysname, fullname);

}

bool PYTHON_break(CBreakpoint *bp){
    return false;
}

bool PYTHON_Command(const char *cmd)
{
    if (!cmd || !strncmp(cmd, "exit()", 6)){
        raise(SIGTERM);
        return true;
    }
    int res = PyRun_SimpleString(cmd);
    return res==0;
}

bool PYTHON_IsDosboxUI(void){
    return dosboxUI;
}

Bitu PYTHON_Loop(bool& dbui){
    dbui = dosboxUI;
    return (Bitu)dbox_loop();
}


void PYTHON_ShutDown(Section* sec){
    if (Py_IsInitialized()) {
        Py_Finalize();
    }
    if (dosboxUI){
        DBGUI_ShutDown();
    }
}

void DEBUG_ShowMsg(char const* format,...){
    va_list msg;
    va_start(msg, format);
    if (dosboxUI){
        DEBUG_ShowMsgV(format, msg);
    }else{
        vprintf(format, msg);
        //printf("\n");
    }
    va_end(msg);
}

void PYTHON_Init(Section* sec){
    sec->AddDestroyFunction(&PYTHON_ShutDown);
    Section_prop * sect=static_cast<Section_prop *>(sec);
    Py_Initialize();
    Py_InspectFlag = true;
    Py_SetProgramName((char*)"dosbox");

    //args 'n' working dir in python paths
    vector<string> args;
    args.push_back(control->cmdline->GetFileName());
    control->cmdline->FillVector(args);
    Property* prop;
    int i=0;
    while ((prop=sect->Get_prop(i++))){
        string p = "--" + prop->propname + "=";
        p += string(prop->GetValue());
        args.push_back(p);
    }

    vector<const char*> argv;
    std::transform(args.begin(), args.end(), back_inserter(argv), [](string& s){ return s.c_str(); });
    PySys_SetArgv((int)argv.size(), (char**)argv.data());

    //plugins path
    string path = sect->Get_string("path");
    if (path.empty()){
        Cross::CreatePlatformConfigDir(path);
        path += "python";
    }
    PyObject* sysPath = PySys_GetObject((char*)"path");
    PyObject* plpath = PyString_FromString(path.c_str());
    PyList_Append(sysPath, plpath);
    Py_DECREF(plpath);

    //init pydosbox
    init_dbox();
    dosboxUI = dbox_start() == 0;
    if (dosboxUI){
        DBGUI_StartUp();
        PyRun_SimpleString("from dosbox import *");
    }
    //TODO: load plugin scripts
}



