/* Generated by Cython 0.27.1 */

#ifndef __PYX_HAVE___dbox
#define __PYX_HAVE___dbox


#ifndef __PYX_HAVE_API___dbox

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

__PYX_EXTERN_C int dbox_start(void);
__PYX_EXTERN_C int dbox_loop(void);
__PYX_EXTERN_C int dbox_exec(char const *);

#endif /* !__PYX_HAVE_API___dbox */

/* WARNING: the interface of the module init function changed in CPython 3.5. */
/* It now returns a PyModuleDef instance instead of a PyModule instance. */

#if PY_MAJOR_VERSION < 3
PyMODINIT_FUNC init_dbox(void);
#else
PyMODINIT_FUNC PyInit__dbox(void);
#endif

#endif /* !__PYX_HAVE___dbox */
