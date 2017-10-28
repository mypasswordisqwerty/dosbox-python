## Config

python section of dosbox config file

```
[python]
#     path: Path to dosbox-python/python directory.
# loglevel: Python log level.
#           Possible values: debug, info, warning, error.
#       ui: Debugger UI module.
#             'dosbox' for internal dosbox ui
#             or name of python module from python/ui directory (pure, gdblike, ...).
#     dasm: Debugger disassembler module.
#             name of python module from python/disasm directory.
#             'dosbox' for dosbox diassembler (located at python/disasm/internal.py so 'internal' is the same).

path=python
loglevel=info
ui=gdblike
dasm=dosbox
```
