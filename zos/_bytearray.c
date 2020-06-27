/*
e=$HOME/miniconda/envs/py38
o='-DNDEBUG -O -qdll -qexportall -qascii -q64 -qnocse -qgonum -qasm -qbitfield=signed -qtarget=zosv2r2 -qarch=10 -qtune=12 -O3 -qstrict -qfloat=ieee:nomaf -qlanglvl=extc1x  -D__MV17195__ -D_XOPEN_SOURCE=600'
xlc_echocmd $o -I$e/include/python3.8 -c -o _bytearray.o _bytearray.c
 */

#ifdef __MVS__
#define _OPEN_SYS_FILE_EXT 1
#endif

#define PY_SSIZE_T_CLEAN
#include "Python.h"
#include <errno.h>
#include <stdio.h>

static PyObject *
bytearray_set_address_size(PyByteArrayObject *module, PyObject *args)
{
  int nbits;
  PyByteArrayObject *self;
  
  if (!PyArg_ParseTuple(args, "Oi:bytearray_set_address_size", &self, &nbits))
    return NULL;
  if (!PyByteArray_Check(self)) {
    PyErr_SetString(PyExc_TypeError, "The first argument must be a bytearray");
    return NULL;
  }
  if (self->ob_exports > 0) {
    PyErr_SetString(PyExc_BufferError,
                    "Existing exports of data: cannot perform set_address_size");
    return 0;
  }
  char *old_addr = self->ob_bytes;
  char *new_addr = NULL;
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
bytearray_buffer_address(PyObject *module, PyObject *args)
{
  PyByteArrayObject *self;
  if (!PyArg_ParseTuple(args, "O:bytearray_buffer_address", &self))
    return NULL;
  if (!PyByteArray_Check(self)) {
    PyErr_SetString(PyExc_TypeError, "The first argument must be a bytearray");
    return NULL;
  }
  return PyLong_FromLong((long)(self->ob_bytes));
}

PyDoc_STRVAR(bytearray_buffer_address__doc__,
"B.buffer_address() -> B\n\
\n\
Returns the addrress of the buffer");


PyDoc_STRVAR(doc, "");

static PyMethodDef _bytearray_methods[] = {
  {"bytearray_set_address_size", (PyCFunction)bytearray_set_address_size, METH_VARARGS, bytearray_set_addresss_size__doc__},
  {"bytearray_buffer_address", (PyCFunction)bytearray_buffer_address, METH_VARARGS, bytearray_buffer_address__doc__},
  {NULL,              NULL}            /* Sentinel */
};

#define INITFUNC PyInit__bytearray
#define MODNAME "_bytearray"

static struct PyModuleDef _bytearraymodule = {
    PyModuleDef_HEAD_INIT,
    MODNAME,
    doc,
    -1,
    _bytearray_methods,
    NULL,
    NULL,
    NULL,
    NULL
};

PyMODINIT_FUNC
INITFUNC(void)
{
  PyObject *m;

    m = PyModule_Create(&_bytearraymodule);
    if (m == NULL)
        return NULL;

    return m;
}
