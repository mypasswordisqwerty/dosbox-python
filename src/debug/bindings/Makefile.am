AM_CPPFLAGS = -I$(top_srcdir)/include

noinst_LIBRARIES = libbindings.a

libbindings_a_SOURCES = empty.cpp

if C_DEBUG_SCRIPTING
libbindings_a_SOURCES = _dbox.cpp _break.cpp
endif
