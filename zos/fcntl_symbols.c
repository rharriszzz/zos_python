/*
e=$HOME/miniconda
o='-DNDEBUG -O -qdll -qexportall -qascii -q64 -qnocse -qgonum -qasm -qbitfield=signed -qtarget=zosv2r2 -qarch=10 -qtune=12 -O3 -qstrict -qfloat=ieee:nomaf -qlanglvl=extc1x  -D__MV17195__ -D_XOPEN_SOURCE=600'
xlc_echocmd $o -I$e/include/python3.7m -c -o fcntl_symbols.o fcntl_symbols.c
 */

#define PY_SSIZE_T_CLEAN
#include "Python.h"
#include <stdio.h>
#include <stdio_ext.h>
#include <errno.h>

static PyMethodDef fcntl_symbols_methods[] = {
  {NULL,              NULL}            /* Sentinel */
};

PyDoc_STRVAR(fcntl_symbols__doc__, "");

static struct PyModuleDef fcntl_symbolsmodule = {
    PyModuleDef_HEAD_INIT,
    "fcntl_symbols",
    fcntl_symbols__doc__,
    -1,
    fcntl_symbols_methods,
    NULL,
    NULL,
    NULL,
    NULL
};


PyMODINIT_FUNC
INITFUNC(void)
{
    PyObject *m, *v;
    PyObject *list;
    const char * const *trace;

    m = PyModule_Create(&fcntl_symbolsmodule);
    if (m == NULL)
        return NULL;

#ifdef F_SETTAG
    if (PyModule_AddIntMacro(m, F_SETTAG)) return NULL;
    if (PyModule_AddIntMacro(m, FT_UNTAGGED)) return NULL;
    if (PyModule_AddIntMacro(m, FT_BINARY)) return NULL;
#endif
#ifdef F_CONTROL_CVT
    if (PyModule_AddIntMacro(m, F_CONTROL_CVT)) return NULL;
    if (PyModule_AddIntMacro(m, SETCVTOFF)) return NULL;
    if (PyModule_AddIntMacro(m, SETCVTON)) return NULL;
    if (PyModule_AddIntMacro(m, SETAUTOCVTON)) return NULL;
    if (PyModule_AddIntMacro(m, QUERYCVT)) return NULL;
#endif
#ifdef SETCVTALL
    if (PyModule_AddIntMacro(m, SETCVTALL)) return NULL;
    if (PyModule_AddIntMacro(m, SETAUTOCVTALL)) return NULL;
#endif

    return m;
}
