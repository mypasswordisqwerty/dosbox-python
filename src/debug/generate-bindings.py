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
mod.add_include('"debug_api.h"')
mod.add_function('ParseCommand', retval('bool'), [param('char*', 'str')])
mod.add_function('DEBUG_ShowMsg', None, [param('char*', 'format')], custom_name='ShowMsg')
mod.add_function('DEBUG_EnableDebugger', None, [], custom_name='EnableDebugger')
mod.add_function('GetAddress', retval('uint32_t'),
	[ param('uint16_t', 'seg'), param('uint32_t','offset') ])

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

mod.header.writeln("""void python_ExecCb(unsigned int hash, void *p);""")
mod.body.writeln("""void python_ExecCb(unsigned int hash, void *p) {
  PyObject *callback = (PyObject*) p;
  PyObject_CallFunction(callback, (char*) "I", hash);
}""")
mod.add_function("python_register_exec_cb",
	None,
	[Parameter.new("PyCallback", "cb", callback='python_ExecCb')],
	custom_name='ListenForExec')

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

mod.header.writeln("""void python_BreakCb(void *p);""")
mod.body.writeln("""void python_BreakCb(void *p) {
  PyObject *callback = (PyObject*) p;
  PyObject_CallFunction(callback, NULL);
}""")
mod.add_function("python_register_break_cb",
	None,
	[Parameter.new("PyCallback", "cb", callback='python_BreakCb')],
	custom_name='RegisterBreak')
mod.add_function("python_unregister_break_cb",
	None,
	[Parameter.new("PyCallback", "cb", callback='python_BreakCb')],
	custom_name='UnregisterBreak')

mod.header.writeln("""void python_LogCb(int tick, const char *logger, char* msg, void *p);""")
mod.body.writeln("""void python_LogCb(int tick, const char *logger, char* msg, void *p) {
  PyObject *callback = (PyObject*) p;
  PyObject_CallFunction(callback, (char*) "iss", tick, logger, msg);
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

klass = mod.add_class('CBreakpoint')
klass.add_method('ShowList', None, [])
klass.add_method('GetIntNr', 'int', [])
klass.add_method('GetSegment', 'int', [])
klass.add_method('GetOffset', 'int', [])
klass.add_method('GetValue', 'int', [])
klass.add_method('IsActive', 'bool', [])

mod.add_container('std::list<CBreakpoint>', retval('CBreakpoint'), 'list')
mod.add_function('python_bpoints', retval('std::list<CBreakpoint>'), [], custom_name='GetBpoints')

mod.add_function('python_vgamode', 'int', [], custom_name='VgaMode')

mod.add_enum('DbgEvt',('CLEANUP','TICK','VSYNC','BREAK','RESUME'),'DBG_')

mod.generate(sys.stdout)

