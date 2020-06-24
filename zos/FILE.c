/*
e=$HOME/miniconda
o='-DNDEBUG -O -qdll -qexportall -qascii -q64 -qnocse -qgonum -qasm -qbitfield=signed -qtarget=zosv2r2 -qarch=10 -qtune=12 -O3 -qstrict -qfloat=ieee:nomaf -qlanglvl=extc1x  -D__MV17195__ -D_XOPEN_SOURCE=600'
xlc_echocmd $o -I$e/include/python3.7m -c -o FILE.o FILE.c
 */

#define PY_SSIZE_T_CLEAN
#include "Python.h"
#include <stdio.h>
#include <stdio_ext.h>
#include <errno.h>

#define FILE_DECLARES \
  int errno_; \
  int errno2_; \
  int error_; \
  int eof_; \
  char amrc_[sizeof(__amrc_type)]; \
  char amrc2_[sizeof(__amrc2_type)];

#define FILE_PROLOG(self, file) \
  Py_BEGIN_ALLOW_THREADS \
  if (file) \
    clearerr(file); \
  errno = 0;

#define FILE_EPILOG(self, file) \
  errno_ = errno; \
  errno2_ = __errno2(); \
  memcpy(amrc_, __amrc, sizeof(__amrc_type)); \
  memcpy(amrc2_, __amrc2, sizeof(__amrc2_type)); \
  if (file) { \
    error_ = ferror(file); \
    eof_ = feof(file); \
  } \
  Py_END_ALLOW_THREADS \
  set_file_error(self, error_, eof_, errno_, errno2_, amrc_, amrc2_)

int set_byte_array(PyObject *self, char *name, char *value, int length)
{
  PyObject *array = PyObject_GetAttrString(self, name);
  memcpy(PyByteArray_AS_STRING(array), value, length);
  return 0;
}

int set_file_error(PyObject *self, int error_, int eof_, int errno_, int errno2_, char *amrc_, char *amrc2_)
{
  PyObject_SetAttrString(self, "error", PyBool_FromLong((long)error_));
  PyObject_SetAttrString(self, "eof", PyBool_FromLong((long)eof_));
  PyObject_SetAttrString(self, "errno", PyLong_FromLong((long)errno_));
  PyObject_SetAttrString(self, "errno2", PyLong_FromLong((long)errno2_));
  set_byte_array(self, "amrc", amrc_, sizeof(__amrc_type));
  set_byte_array(self, "amrc2", amrc2_, sizeof(__amrc2_type));
  return -1;
}

static PyObject *
FILE___init__(PyObject *self, PyObject *args, PyObject *kwargs)
{
    static const char * const _keywords[] = {"file", "mode", "locking", NULL};
    static _PyArg_Parser _parser = {"O|Op:FILE", _keywords, 0};
    PyObject *name_obj;
    const char *name;
    PyObject *mode_obj = Py_None;
    const char *mode;
    int locking = 0;
    FILE *file = NULL;
    int readable = 0;
    int writable = 0;
    FILE_DECLARES;
    
    if (!_PyArg_ParseTupleAndKeywordsFast(args, kwargs, &_parser,
                                          &name_obj, &mode_obj, &locking)) {
      return NULL;
    }
    PyObject_SetAttrString(self, "name", name_obj);
    name = PyUnicode_AsUTF8(name_obj);
    if (PyUnicode_Check(mode_obj)) {
      mode = PyUnicode_AsUTF8(mode_obj);
    } else {
      mode = "r";
      mode_obj = PyUnicode_FromString(mode);
    }
    PyObject_SetAttrString(self, "mode", mode_obj);
    PyObject_SetAttrString(self, "amrc", PyByteArray_FromStringAndSize(amrc_, sizeof(amrc_)));
    PyObject_SetAttrString(self, "amrc2", PyByteArray_FromStringAndSize(amrc2_, sizeof(amrc2_)));
    FILE_PROLOG(self, file);
    file = fopen(name, mode);
    FILE_EPILOG(self, file);
    if (file) {
      Py_BEGIN_ALLOW_THREADS
        __fsetlocking(file, locking ? FSETLOCKING_INTERNAL : FSETLOCKING_BYCALLER);
      readable = __freadable(file);
      writable = __fwritable(file);
      Py_END_ALLOW_THREADS
    }
    PyObject_SetAttrString(self, "file", PyLong_FromLong((long)file));
    PyObject_SetAttrString(self, "readable", PyBool_FromLong(readable));
    PyObject_SetAttrString(self, "writable", PyBool_FromLong(writable));
    Py_RETURN_NONE;
}

PyObject *
FILE_fclose(PyObject *self)
{
  int result;
  FILE_DECLARES;
  PyObject *file_obj = PyObject_GetAttrString(self, "file");
  if (file_obj == Py_None)
    Py_RETURN_NONE;
  FILE *file = (FILE *)PyLong_AsLong(file_obj);
  FILE_PROLOG(self, file);
  result = fclose(file);
  FILE_EPILOG(self, 0);
  if (PyObject_SetAttrString(self, "file", Py_None))
    return NULL;
  Py_DECREF(file_obj);
  file_obj = Py_None;
  Py_INCREF(file_obj);
  return PyLong_FromLong(result);
}

PyObject *
FILE_fileno(PyObject *self)
{
  int result;
  FILE_DECLARES;
  PyObject *file_obj = PyObject_GetAttrString(self, "file");
  if (file_obj == Py_None)
    Py_RETURN_NONE;
  FILE *file = (FILE *)PyLong_AsLong(file_obj);
  FILE_PROLOG(self, file);
  result = fileno(file);
  FILE_EPILOG(self, file);
  return PyLong_FromLong(result);
}

PyObject *
FILE_fflush(PyObject *self) // METH_NOARGS
{
  int result;
  FILE_DECLARES;
  PyObject *file_obj = PyObject_GetAttrString(self, "file");
  if (file_obj == Py_None)
    Py_RETURN_NONE;
  FILE *file = (FILE *)PyLong_AsLong(file_obj);
  FILE_PROLOG(self, file);
  result = fflush(file);
  FILE_EPILOG(self, file);
  return PyLong_FromLong(result);
}

PyObject *
FILE_fread(PyObject *self, PyObject *args) // METH_VARARGS
{
  int result;
  Py_buffer *buffer;
  FILE_DECLARES;
  PyObject *file_obj = PyObject_GetAttrString(self, "file");
  if (file_obj == Py_None)
    Py_RETURN_NONE;
  if (!PyArg_ParseTuple(args, "y*:fread", &buffer))
    return NULL;
  FILE *file = (FILE *)PyLong_AsLong(file_obj);
  FILE_PROLOG(self, file);
  result = fread(buffer->buf, buffer->len, 1, file);
  FILE_EPILOG(self, file);
  Py_buffer_Release(buffer);
  return PyLong_FromLong(result);
}

PyObject *
FILE_fwrite(PyObject *self, PyObject *args) // METH_VARARGS
{
  int result;
  Py_buffer *buffer;
  FILE_DECLARES;
  PyObject *file_obj = PyObject_GetAttrString(self, "file");
  if (file_obj == Py_None)
    Py_RETURN_NONE;
  if (!PyArg_ParseTuple(args, "y*:fread", &buffer))
    return NULL;
  FILE *file = (FILE *)PyLong_AsLong(file_obj);
  FILE_PROLOG(self, file);
  result = fwrite(buffer->buf, buffer->len, 1, file);
  FILE_EPILOG(self, file);
  Py_buffer_Release(buffer);
  return PyLong_FromLong(result);
}

PyObject *
FILE_rewind(PyObject *self) // METH_NOARGS
{
  int result = 0;
  FILE_DECLARES;
  PyObject *file_obj = PyObject_GetAttrString(self, "file");
  if (file_obj == Py_None)
    Py_RETURN_NONE;
  FILE *file = (FILE *)PyLong_AsLong(file_obj);
  FILE_PROLOG(self, file);
  rewind(file);
  FILE_EPILOG(self, file);
  return PyLong_FromLong(result);
}

PyObject *
FILE_fgetpos(PyObject *self, PyObject *args) // METH_VARARGS
{
  int result;
  Py_buffer buffer;
  FILE_DECLARES;
  PyObject *file_obj = PyObject_GetAttrString(self, "file");
  if (file_obj == Py_None)
    Py_RETURN_NONE;
  if (!PyArg_ParseTuple(args, "y*:fread", &buffer))
    return NULL;
  if (buffer.len < sizeof(fpos_t) || buffer.readonly) {
    return NULL;
  }
  FILE *file = (FILE *)PyLong_AsLong(file_obj);
  FILE_PROLOG(self, file);
  result = fgetpos(file, (fpos_t *)buffer.buf);
  FILE_EPILOG(self, file);
  return PyLong_FromLong(result);
}

PyObject *
FILE_fsetpos(PyObject *self, PyObject *args) // METH_VARARGS
{
  int result;
  Py_buffer buffer;
  FILE_DECLARES;
  PyObject *file_obj = PyObject_GetAttrString(self, "file");
  if (file_obj == Py_None)
    Py_RETURN_NONE;
  if (!PyArg_ParseTuple(args, "y*:fread", &buffer))
    return NULL;
  if (buffer.len < sizeof(fpos_t)) {
    return NULL;
  }
  FILE *file = (FILE *)PyLong_AsLong(file_obj);
  FILE_PROLOG(self, file);
  result = fsetpos(file, (fpos_t *)buffer.buf);
  FILE_EPILOG(self, file);
  return PyLong_FromLong(result);
}

PyObject *
FILE_fldata(PyObject *self, PyObject *args) // METH_VARARGS
{
  int result;
  Py_buffer buffer;
  FILE_DECLARES;
  PyObject *file_obj = PyObject_GetAttrString(self, "file");
  if (file_obj == Py_None)
    Py_RETURN_NONE;
  if (!PyArg_ParseTuple(args, "y*:fread", &buffer))
    return NULL;
  if (buffer.len < sizeof(fldata_t) || buffer.readonly) {
    return NULL;
  }
  FILE *file = (FILE *)PyLong_AsLong(file_obj);
  FILE_PROLOG(self, file);
  result = fldata(file, NULL, (fldata_t *)buffer.buf);
  FILE_EPILOG(self, file);
  return PyLong_FromLong(result);
}

PyObject *
FILE_flocate(PyObject *self, PyObject *args) // METH_VARARGS
{
  int result;
  Py_buffer buffer;
  int options = 0;
  FILE_DECLARES;
  PyObject *file_obj = PyObject_GetAttrString(self, "file");
  if (file_obj == Py_None)
    Py_RETURN_NONE;
  if (!PyArg_ParseTuple(args, "y*i:fread", &buffer, options))
    return NULL;
  FILE *file = (FILE *)PyLong_AsLong(file_obj);
  FILE_PROLOG(self, file);
  result = flocate(file, buffer.buf, buffer.len, options);
  FILE_EPILOG(self, file);
  return PyLong_FromLong(result);
}

PyObject *
FILE_fdelrec(PyObject *self)  // METH_NOARGS
{
  int result;
  FILE_DECLARES;
  PyObject *file_obj = PyObject_GetAttrString(self, "file");
  if (file_obj == Py_None)
    Py_RETURN_NONE;
  FILE *file = (FILE *)PyLong_AsLong(file_obj);
  FILE_PROLOG(self, file);
  result = fdelrec(file);
  FILE_EPILOG(self, file);
  return PyLong_FromLong(result);
}

PyObject *
FILE_fupdate(PyObject *self, PyObject *args) // METH_VARARGS
{
  int result;
  Py_buffer buffer;
  FILE_DECLARES;
  PyObject *file_obj = PyObject_GetAttrString(self, "file");
  if (file_obj == Py_None)
    Py_RETURN_NONE;
  if (!PyArg_ParseTuple(args, "y*:fread", &buffer))
    return NULL;
  FILE *file = (FILE *)PyLong_AsLong(file_obj);
  FILE_PROLOG(self, file);
  result = fupdate(buffer.buf, buffer.len, file);
  FILE_EPILOG(self, file);
  return PyLong_FromLong(result);
}

PyDoc_STRVAR(doc, "");

static PyMethodDef FILE_methods[] = {
  {"FILE___init__", FILE___init__, METH_FASTCALL | METH_KEYWORDS, doc},
  {"FILE_fclose", FILE_fclose, METH_NOARGS, doc},
  {"FILE_fileno", FILE_fileno, METH_NOARGS, doc},
  {"FILE_fflush", FILE_fflush, METH_NOARGS, doc},
  {"FILE_fread", FILE_fread,  METH_VARARGS, doc},
  {"FILE_fwrite", FILE_fwrite, METH_VARARGS, doc},
  {"FILE_rewind", FILE_rewind, METH_NOARGS, doc},
  {"FILE_fgetpos", FILE_fgetpos, METH_VARARGS, doc},
  {"FILE_fsetpos", FILE_fsetpos, METH_VARARGS, doc},
  {"FILE_fldata", FILE_fldata, METH_VARARGS, doc},
  {"FILE_flocate", FILE_flocate, METH_VARARGS, doc},
  {"FILE_fdelrec", FILE_fdelrec, METH_NOARGS, doc},
  {"FILE_fupdate", FILE_fupdate, METH_VARARGS, doc},
  {NULL,              NULL}            /* Sentinel */
};

static char *FILE__doc__="";

static struct PyModuleDef FILEmodule = {
    PyModuleDef_HEAD_INIT,
    "FILE",
    doc, /* FILE__doc__ */
    -1,
    FILE_methods,
    NULL,
    NULL,
    NULL,
    NULL
};

#define FPOS_SIZE sizeof(fpos_t)
#define FLDATA_SIZE sizeof(fldata_t)


PyMODINIT_FUNC
INITFUNC(void)
{
    PyObject *m, *v;
    PyObject *list;
    const char * const *trace;

    m = PyModule_Create(&FILEmodule);
    if (m == NULL)
        return NULL;

    if (PyModule_AddIntMacro(m, FPOS_SIZE)) return NULL;
    if (PyModule_AddIntMacro(m, FLDATA_SIZE)) return NULL;
#ifdef __RBA_EQ
    if (PyModule_AddIntMacro(m, __RBA_EQ)) return NULL;
    if (PyModule_AddIntMacro(m, __KEY_FIRST)) return NULL;
    if (PyModule_AddIntMacro(m, __KEY_LAST)) return NULL;
    if (PyModule_AddIntMacro(m, __KEY_EQ)) return NULL;
    if (PyModule_AddIntMacro(m, __KEY_EQ_BWD)) return NULL;
    if (PyModule_AddIntMacro(m, __KEY_GE)) return NULL;
    if (PyModule_AddIntMacro(m, __RBA_EQ_BWD)) return NULL;
#endif
    return m;
}
