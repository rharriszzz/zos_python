/*
e=$HOME/miniconda/envs/py38
o='-DNDEBUG -O -qdll -qexportall -qascii -q64 -qnocse -qgonum -qasm -qbitfield=signed -qtarget=zosv2r2 -qarch=10 -qtune=12 -O3 -qstrict -qfloat=ieee:nomaf -qlanglvl=extc1x  -D__MV17195__ -D_XOPEN_SOURCE=600'
xlc_echocmd $o -I$e/include/python3.8 -c -o _system_call.o _system_call.c
*/

#define PY_SSIZE_T_CLEAN

#include "Python.h"


PyDoc_STRVAR(_system_call__doc__,
	     "The module _system_call contains the function zos_system_call.");

PyDoc_STRVAR(zos_system_call__doc__,
"B.zos_system_call() -> B\n\
\n\
See the examples in this directory.");

/* r15, r0, r1, code_or_save, type */
#define SYSTEM_CALL__SVC    1
#define SYSTEM_CALL__PC     2
#define SYSTEM_CALL__CALL   3
#define SYSTEM_CALL__CALL31 4
       
static PyObject *
zos_system_call(PyObject *module, PyObject *args)
{
  Py_ssize_t byteslen;
  const char *bytesptr;
  Py_buffer buffer;
  if (!PyArg_ParseTuple(args, "w*:zos_system_call", &buffer))
      return NULL;

  bytesptr = (const char *) buffer.buf;
  byteslen = buffer.len;

  long type = ((long *)bytesptr)[4];
  Py_BEGIN_ALLOW_THREADS
  if (type == SYSTEM_CALL__SVC) {
    __asm__
      (" LMG   15,2,0(%0) \n"
       " LARL  3,*+10     \n"
       " BRC   X'F',*+6   \n"
       " SVC   0          \n"
       " EX    2,0(0,3)   \n"
       " STMG  15,1,0(%0) \n"
       : : "a"(bytesptr) : "r0", "r1", "r2", "r3", "r14", "r15");
  } else if (type == SYSTEM_CALL__PC) {
    __asm__
      (" LMG   15,2,0(%0) \n"
       " LAM   15,1,40(%0)\n"
       " LGR   14,2       \n"
       " PC    0(14)      \n"
       " STMG  15,1,0(%0) \n"
       : : "a"(bytesptr) : "r0", "r1", "r2", "r14", "r15");
  } else if (type == SYSTEM_CALL__CALL) {
    __asm__
      (" LMG   15,2,0(%0) \n"
       " LGR   13,2       \n"
       " BALR  14,15      \n"
       " STMG  15,1,0(%0) \n"
       : : "a"(bytesptr) : "r0", "r1", "r2", "r13", "r14", "r15"); 
  } else if (type == SYSTEM_CALL__CALL31) {
    __asm__
      (" LMG   15,2,0(%0) \n"
       " LGR   13,2       \n"
       " SAM31            \n"
       " BALR  14,15      \n"
       " SAM64            \n"
       " LLGFR 15,15      \n"
       " LLGFR 0,0        \n"
       " LLGFR 1,1        \n"
       " STMG  15,1,0(%0) \n"
       : : "a"(bytesptr) : "r0", "r1", "r2", "r13", "r14", "r15");
  }
  Py_END_ALLOW_THREADS
  PyBuffer_Release(&buffer);
  Py_RETURN_NONE;
}

static PyMethodDef _system_call_methods[] = {
    {"zos_system_call", zos_system_call, METH_VARARGS, zos_system_call__doc__},
    {NULL,              NULL}            /* Sentinel */
};

static int
all_ins(PyObject *m)
{
    if (PyModule_AddIntMacro(m, SYSTEM_CALL__SVC)) return -1;
    if (PyModule_AddIntMacro(m, SYSTEM_CALL__PC)) return -1;
    if (PyModule_AddIntMacro(m, SYSTEM_CALL__CALL)) return -1;
    if (PyModule_AddIntMacro(m, SYSTEM_CALL__CALL31)) return -1;
    return 0;
}


#define INITFUNC PyInit__system_call
#define MODNAME "_system_call"

static struct PyModuleDef _system_callmodule = {
    PyModuleDef_HEAD_INIT,
    MODNAME,
    _system_call__doc__,
    -1,
    _system_call_methods,
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

    m = PyModule_Create(&_system_callmodule);
    if (m == NULL)
        return NULL;

    if (all_ins(m))
        return NULL;

    return m;
}

#ifdef __cplusplus
}
#endif
