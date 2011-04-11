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

mod.header.writeln("""void _wrap_Callback(void *p);""")
mod.body.writeln("""void _wrap_Callback(void *p) {
  PyObject *callback = (PyObject*) p;
  PyObject_CallFunction(callback, NULL);
}""")
mod.add_function("python_register_tick_cb",
	None,
	[Parameter.new("PyCallback", "cb", callback='_wrap_Callback')],
	custom_name='RegisterTick')
mod.add_function("python_unregister_tick_cb",
	None,
	[Parameter.new("PyCallback", "cb", callback='_wrap_Callback')],
	custom_name='UnregisterTick')

mod.add_function('python_registers',
	retval('PyObject*',caller_owns_return=True), [],
	custom_name='GetRegs')
mod.add_function('python_dasm',
	retval('char*'),
	[ param('uint16_t','seg'),param('uint32_t','ofs'),param('int','eip') ],
	custom_name='disasm')

mod.add_function('python_memory', None,
	[ param('uint16_t','seg'),param('uint32_t','ofs'),param('uint32_t','len'),
	param('std::string*','mem', direction=Parameter.DIRECTION_OUT) ],
	custom_name='ReadMem')

mod.header.writeln("""void _wrap_LogCb(int tick, const char *logger, char* msg, void *p);""")
mod.body.writeln("""void _wrap_LogCb(int tick, const char *logger, char* msg, void *p) {
  PyObject *callback = (PyObject*) p;
  PyObject_CallFunction(callback, (char*) "iss", tick, logger, msg);
}""")
mod.add_function("python_register_log_cb",
	None,
	[Parameter.new("PyCallback", "cb", callback='_wrap_LogCb')],
	custom_name='RegisterLog')
mod.add_function("python_unregister_log_cb",
	None,
	[Parameter.new("PyCallback", "cb", callback='_wrap_LogCb')],
	custom_name='UnregisterLog')


klass = mod.add_class('CBreakpoint')
klass.add_method('ShowList', None, [])
klass.add_method('GetIntNr', 'int', [])
klass.add_method('GetSegment', 'int', [])
klass.add_method('GetOffset', 'int', [])
klass.add_method('GetValue', 'int', [])
klass.add_method('IsActive', 'bool', [])

mod.add_container('std::list<CBreakpoint>', retval('CBreakpoint'), 'list')
mod.add_function('python_bpoints', retval('std::list<CBreakpoint>'), [], custom_name='GetBpoints')

mod.generate(sys.stdout)

