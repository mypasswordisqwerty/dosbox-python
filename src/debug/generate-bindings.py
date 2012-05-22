#!/usr/bin/python
import sys
from pybindgen import *
from pybindgen.typehandlers.base import ForwardWrapperBase

class PyCallbackParam(Parameter):
	DIRECTIONS = [Parameter.DIRECTION_IN]
	CTYPES = ['PyCallback']
	CALLBACK = None

	def __init__(self, ctype, name, direction=Parameter.DIRECTION_IN, is_const=False, default_value=None, callback=None):
		self.CALLBACK = callback
		super(PyCallbackParam, self).__init__(ctype, name, direction, is_const, default_value)

	def convert_python_to_c(self, wrapper):
		assert isinstance(wrapper, ForwardWrapperBase)
		assert self.CALLBACK != None

		py_cb = wrapper.declarations.declare_variable("PyObject*", self.name)
		wrapper.parse_params.add_parameter('O', ['&'+py_cb], self.name)

		wrapper.before_call.write_error_check("!PyCallable_Check(%s)" % py_cb,
			"""PyErr_SetString(PyExc_TypeError, "visitor parameter must be callable");""")
		wrapper.call_params.append(self.CALLBACK)
		wrapper.before_call.write_code("Py_INCREF(%s);" % py_cb)
		wrapper.before_call.add_cleanup_code("Py_DECREF(%s);" % py_cb)
		wrapper.call_params.append(py_cb)

	def convert_c_to_python(self, wrapper):
		raise NotImplementedError

"""
from pybindgen.gccxmlparser import ModuleParser
module_parser = ModuleParser('dosboxdbg', '::')
module = module_parser.parse([sys.argv[1]])
module.add_include('"debug_api.h"')
pybindgen.write_preamble(FileCodeSink(sys.stdout))
module.generate(FileCodeSink(sys.stdout))
"""

mod = Module('dosboxdbg')
mod.add_include('"../../config.h"')
mod.add_include('"debug_api.h"')
mod.add_function('ParseCommand', retval('bool'), [param('char*', 'str')])
mod.add_function('DEBUG_ShowMsg', None, [param('char*', 'format')], custom_name='ShowMsg')
mod.add_function('DEBUG_EnableDebugger', None, [], custom_name='EnableDebugger')
mod.add_function('GetAddress', retval('uint32_t'),
	[ param('uint16_t', 'seg'), param('uint32_t','offset') ])

klass = mod.add_class('CBreakpoint')
klass.add_method('ShowList', None, [])
klass.add_method('GetIntNr', 'int', [])
klass.add_method('GetLocation', 'unsigned long', [])
klass.add_method('GetSegment', 'int', [])
klass.add_method('GetOffset', 'unsigned long', [])
klass.add_method('GetValue', 'int', [])
klass.add_method('IsActive', 'bool', [])

mod.add_function('python_getscriptdir', 'std::string', [], custom_name='GetScriptDir')

mod.header.writeln("""void python_EventCb(void *p);""")
mod.body.writeln("""void python_EventCb(void *p) {
  PyObject *callback = (PyObject*) p;
  PyObject_CallFunction(callback, NULL);
}""")
mod.add_function("python_register_event_cb",
	None,
	[param('int','type'),Parameter.new("PyCallback", "cb", callback='python_EventCb')],
	custom_name='ListenFor')
mod.add_function("python_unregister_event_cb",
	None,
	[param('int','type'),Parameter.new("PyCallback", "cb", callback='python_EventCb')],
	custom_name='DontListenFor')

mod.header.writeln("""bool python_ExecCb(const char *file, void *p);""")
mod.body.writeln("""bool python_ExecCb(const char *file, void *p) {
  PyObject *callback = (PyObject*) p;
  PyObject_CallFunction(callback, (char*) "s", file);
  return true;
}""")
mod.add_function("python_register_exec_cb",
	None,
	[Parameter.new("PyCallback", "cb", callback='python_ExecCb')],
	custom_name='ListenForExec')

mod.header.writeln("""bool python_CliCmdCb(const char *cmd, void *p);""")
mod.body.writeln("""
bool python_CliCmdCb(const char *cmd, void *p) {
  PyObject *callback = (PyObject*) p;
	PyObject *result = PyObject_CallFunction(callback, (char*) "s", cmd);
	if (result == NULL) return false;
  bool ret = PyObject_IsTrue(result);
	Py_DECREF(result);
	return ret;
}""")
mod.add_function("python_register_clicmd_cb",
	None,
	[Parameter.new("PyCallback", "cb", callback='python_CliCmdCb')],
	custom_name='ListenForCmd')

mod.add_function('python_registers',
	retval('PyObject*',caller_owns_return=False), [],
	custom_name='GetRegs')
mod.add_function('python_segments',
	retval('PyObject*',caller_owns_return=False), [],
	custom_name='GetSegments')

mod.add_function('python_dasm',
	retval('char*'),
	[ param('uint16_t','seg'),param('uint32_t','ofs'),param('int','eip') ],
	custom_name='disasm')

mod.add_function('python_mcbs', retval('PyObject*',caller_owns_return=False), [],
	custom_name='GetMCBs')

mod.add_function('python_getmemory', None,
	[ param('uint32_t','loc'),param('uint32_t','len'),
	param('std::string*','mem', direction=Parameter.DIRECTION_OUT) ],
	custom_name='ReadMem')
mod.add_function('python_setmemory', None,
	[ param('uint32_t','loc'),
	param('std::string*','mem', direction=Parameter.DIRECTION_IN) ],
	custom_name='WriteMem')

mod.add_function('python_getvidmemory', None,
	[ param('uint16_t','x'),param('uint32_t','y'),
	param('uint16_t','w'),param('uint32_t','h'), param('uint8_t','page'),
	param('std::string*','mem', direction=Parameter.DIRECTION_OUT) ],
	custom_name='ReadVidMem')

mod.add_function('python_setvidmemory', None,
	[ param('uint16_t','x'),param('uint32_t','y'),
	param('uint16_t','w'),param('uint32_t','h'), param('uint8_t','page'),
	param('std::string*','mem', direction=Parameter.DIRECTION_IN) ],
	custom_name='WriteVidMem')

mod.add_function('python_getpalette', None,
	[ param('std::string*','mem', direction=Parameter.DIRECTION_OUT) ],
	custom_name='GetPalette')
mod.add_function('python_setpalette', None,
	[ param('std::string*','mem', direction=Parameter.DIRECTION_IN) ],
	custom_name='SetPalette')

mod.header.writeln("""bool python_BreakCb(CBreakpoint *bp, void *p);""")
mod.body.writeln("""bool python_BreakCb(CBreakpoint *bp, void *p) {
  PyObject *callback = (PyObject*) p;
  PyCBreakpoint *py_CBreakpoint;
  py_CBreakpoint = PyObject_New(PyCBreakpoint, &PyCBreakpoint_Type);
  py_CBreakpoint->flags = PYBINDGEN_WRAPPER_FLAG_NONE;
  py_CBreakpoint->obj = bp;
  return PyObject_CallFunction(callback, (char*) "O", py_CBreakpoint) != Py_False;
}""")
mod.add_function("python_register_break_cb",
	None,
	[Parameter.new("PyCallback", "cb", callback='python_BreakCb')],
	custom_name='RegisterBreak')
mod.add_function("python_unregister_break_cb",
	None,
	[Parameter.new("PyCallback", "cb", callback='python_BreakCb')],
	custom_name='UnregisterBreak')

mod.header.writeln("""bool python_LogCb(int tick, const char *logger, char* msg, void *p);""")
mod.body.writeln("""
bool python_LogCb(int tick, const char *logger, char* msg, void *p) {
  PyObject *callback = (PyObject*) p;
  return PyObject_CallFunction(callback, (char*) "iss", tick, logger, msg) != Py_False;
}""")
mod.add_function("python_register_log_cb",
	None,
	[Parameter.new("PyCallback", "cb", callback='python_LogCb')],
	custom_name='ListenForLog')
mod.add_function("python_unregister_log_cb",
	None,
	[Parameter.new("PyCallback", "cb", callback='python_LogCb')],
	custom_name='DontListenForLog')

#s_vga_gfx = mod.add_struct('VGA_Gfx')
#s_vga_gfx.add_instance_attribute('mode', 'int')
#s_vga_config = mod.add_struct('VGA_Config')
#s_vga_config.add_instance_attribute('display_start', 'int')
#s_vga_config.add_instance_attribute('gfx', 'VGA_Gfx')

mod.add_container('std::list<CBreakpoint>', retval('CBreakpoint'), 'list')
mod.add_function('python_bpoints', retval('std::list<CBreakpoint>'), [], custom_name='GetBPs')

mod.add_function('python_vgamode', 'int', [], custom_name='VgaMode')

klass = mod.add_class('CDebugVar')
klass.add_copy_constructor()
klass.add_constructor([param('char*','name'), param('unsigned long','addr')])
klass.add_method('GetName', 'char*', [])
klass.add_method('GetAdr', 'unsigned long', [])

mod.add_container('std::list<CDebugVar>', retval('CDebugVar'), 'list')
mod.add_function('python_vars', retval('std::list<CDebugVar>'), [], custom_name='GetVars')
mod.add_function('python_insertvar', None, [param('char*','name'), param('unsigned long','addr')], custom_name='InsertVar')

mod.add_function('PMurHash32_File', 'unsigned int', [param('int','seed'),param('char*','filename')])
#uint32_t PMurHash32(uint32_t seed, const void *key, int len)
mod.add_enum('DbgEvt',('CLEANUP','TICK','VSYNC','BREAK','RESUME'),'DBG_')

with open('pybinding.cpp','w') as fh:
  mod.generate(fh)
