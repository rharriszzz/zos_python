/*
e=$HOME/miniconda
o='-DNDEBUG -O -qdll -qexportall -qascii -q64 -qnocse -qgonum -qasm -qbitfield=signed -qtarget=zosv2r2 -qarch=10 -qtune=12 -O3 -qstrict -qfloat=ieee:nomaf -qlanglvl=extc1x  -D__MV17195__ -D_XOPEN_SOURCE=600'
xlc_echocmd $o -I$e/include/python3.7m -c -o _zos.o _zos.c
 */

#ifdef __MVS__
#define _OPEN_SYS_FILE_EXT 1
#endif

#define PY_SSIZE_T_CLEAN
#include "Python.h"
#include <errno.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/modes.h>

static PyObject *
path_error(PyObject *module, char *path, int errno_, int errno2_)
{
  return NULL; /* PyErr_SetFromErrnoWithFilenameObject(PyExc_OSError, path); */
}

static PyObject *
_stat_internal(PyObject *module, PyObject *args)
{
  int result;
  char *path;
  Py_buffer stat_buffer;

  if (!PyArg_ParseTuple(args, "sy*:_stat_internal", &path, &stat_buffer))
    return NULL;

  Py_BEGIN_ALLOW_THREADS
    result = stat(path, (struct stat *)stat_buffer.buf);
  Py_END_ALLOW_THREADS

    if (result != 0)
      return path_error(module, path, errno, __errno2());

  Py_buffer_Release(stat_buffer);
  return PyLong_FromLong(result);
}

static PyObject *
_chattr_internal(PyObject *module, PyObject *args)
{
  int result;
  char *path;
  Py_buffer chattr_buffer;

  if (!PyArg_ParseTuple(args, "sy*:_stat_internal", &path, &chattr_buffer))
    return NULL;

  Py_BEGIN_ALLOW_THREADS
    result = __chattr(path, (attrib_t *)chattr_buffer.buf, chattr_buffer.len);
  Py_END_ALLOW_THREADS

    if (result != 0) 
        return path_error(module, path, errno, __errno2());

  Py_buffer_Release(chattr_buffer);
  return PyLong_FromLong(result);
}

static PyObject *
bytearray_set_address_size(PyByteArrayObject *self, PyObject *arg)
{
  int nbits;

  if (self->ob_exports > 0) {
    PyErr_SetString(PyExc_BufferError,
                    "Existing exports of data: cannot perform set_address_size");
    return 0;
  }
  if (!PyArg_Parse(arg, "i:setaddress_size", &nbits)) {
    return 0;
  }
  void *new_addr = NULL;
  size_t size;
  if (nbits == 24) {
    new_addr = __malloc24(self->ob_alloc);
  } else if (nbits == 31) {
    new_addr = __malloc31(self->ob_alloc);
  } else {
    new_addr = PyObject_Malloc(self->ob_alloc);
  }
  if (new_addr == NULL) {
    PyErr_SetString(PyExc_BufferError,
                    "Callot allocate");
    return NULL;
  }
  void *old_addr = self->ob_bytes;
  memcpy(new_addr, old_addr, self->ob_alloc);
  self->ob_bytes = new_addr;
  self->ob_start += (new_addr - old_addr);
  PyObject_Free(old_addr);
    
  Py_INCREF(self);
  return (PyObject *)self;
}

PyDoc_STRVAR(bytearray_set_addresss_size__doc__,
"B.set_address_size(nbits) -> B\n\
\n\
Ensures that the bytearray's buffer is addressable with an address of size nbits.\n\
Any value other than 24 or 31 is equivalent to 0 meaning 64 bits.");


static PyObject *
bytearray_buffer_address(PyByteArrayObject *self)
{
    return PyLong_FromLong((long)(self->ob_bytes));
}

PyDoc_STRVAR(bytearray_buffer_address__doc__,
"B.buffer_address() -> B\n\
\n\
Returns the addrress of the buffer");


PyDoc_STRVAR(_zos_system_call__doc__,
"B.zos_system_call() -> B\n\
\n\
");

/* r15, r0, r1, code_or_save, type */
#define SYSTEM_CALL__SVC    1
#define SYSTEM_CALL__PC     2
#define SYSTEM_CALL__CALL   3
#define SYSTEM_CALL__CALL31 4
       
static PyObject *
_system_call(PyObject *self, PyObject *args)
{
  Py_ssize_t byteslen;
  const char *bytesptr;
  Py_buffer buffer;
  if (!PyArg_ParseTuple(args, "w*:zos_system_call", &buffer))
      return NULL;

  bytesptr = (const char *) buffer.buf;
  byteslen = buffer.len;

  long type = ((long *)bytesptr)[4];
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

  Py_buffer_Release(&buffer);
  Py_RETURN_NONE;
}

PyDoc_STRVAR(doc, "");

static PyMethodDef _zos_methods[] = {
  {"_stat_internal",   _stat_internal,  METH_VARARGS, doc},
  {"_chattr_internal", _chattr_internal,METH_VARARGS, doc},
  {"_system_call", _system_call, METH_VARARGS, doc},
  {"bytearray_set_address_size", (PyCFunction)bytearray_set_address_size, METH_O, bytearray_set_addresss_size__doc__},
  {"bytearray_buffer_address", (PyCFunction)bytearray_buffer_address, METH_NOARGS, bytearray_buffer_address__doc__},
  {NULL,              NULL}            /* Sentinel */
};

static struct PyModuleDef _zosmodule = {
    PyModuleDef_HEAD_INIT,
    "_zos",
    doc,
    -1,
    _zos_methods,
    NULL,
    NULL,
    NULL,
    NULL
};

#define STAT_SIZE sizeof(struct stat)
#define ATTRIB_SIZE sizeof(attrib_t)

MODINIT_FUNC
PyInit__zos(void)
{
  PyObject *m;

    m = PyModule_Create(&_zosmodule);
    if (m == NULL)
        return NULL;

    if (PyModule_AddIntMacro(m, STAT_SIZE)) return NULL;
    if (PyModule_AddIntMacro(m, ATTRIB_SIZE)) return NULL;
    if (PyModule_AddIntMacro(m, SYSTEM_CALL__SVC)) return NULL;
    if (PyModule_AddIntMacro(m, SYSTEM_CALL__PC)) return NULL;
    if (PyModule_AddIntMacro(m, SYSTEM_CALL__CALL)) return NULL;
    if (PyModule_AddIntMacro(m, SYSTEM_CALL__CALL31)) return NULL;

    return m;
}
