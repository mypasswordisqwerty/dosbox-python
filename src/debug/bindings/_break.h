/* Generated by Cython 0.27.1 */

#ifndef __PYX_HAVE___break
#define __PYX_HAVE___break


#ifndef __PYX_HAVE_API___break

#ifndef __PYX_EXTERN_C
  #ifdef __cplusplus
    #define __PYX_EXTERN_C extern "C"
  #else
    #define __PYX_EXTERN_C extern
  #endif
#endif

#ifndef DL_IMPORT
  #define DL_IMPORT(_T) _T
#endif

__PYX_EXTERN_C int break_run(CBreakpoint *);

#endif /* !__PYX_HAVE_API___break */

/* WARNING: the interface of the module init function changed in CPython 3.5. */
/* It now returns a PyModuleDef instance instead of a PyModule instance. */

#if PY_MAJOR_VERSION < 3
PyMODINIT_FUNC init_break(void);
#else
PyMODINIT_FUNC PyInit__break(void);
#endif

#endif /* !__PYX_HAVE___break */
