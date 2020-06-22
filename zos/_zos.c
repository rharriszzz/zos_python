#define PY_SSIZE_T_CLEAN
#include "Python.h"
#include <stdio.h>
#include <errno.h>

#define FILE_DECLARES \
  int errno_; \
  int errno2_; \
  int error_; \
  int eof; \
  char amrc_[sizeof(__amrc_type)]; \
  char amrc2_[sizeof(__amrc2_type)];

#define FILE_PROLOG(self, file) \
  Py_BEGIN_ALLOW_THREADS \
  if (file) \
    clearerr(file); \
  errno = 0;

#define FILE_EPILOG(self, file) \
  errno_ = errno; \
  errno2_ = __errno2; \
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

int set_file_error(PyObject *self, int error_, int eof_, int errno_, int erron2_, char *amrc_, char *amrc2_)
{
  PyObject_SetAttrString(self, "error", PyBool_FromLong((long)error));
  PyObject_SetAttrString(self, "eof", PyBool_FromLong((long)eof));
  PyObject_SetAttrString(self, "errno", PyLong_FromLong((long)errno_));
  PyObject_SetAttrString(self, "errno2", PyLong_FromLong((long)errno2_));
  set_byte_array(self, "amrc", amrc_, sizeof(__amrc_type));
  set_byte_array(self, "amrc2", amrc2_, sizeof(__amrc2_type));
  return -1;
}

static PyObject *
FILE___init__(PyObject *self, PyObject *args, PyObject *kwargs)
{
    int return_value = -1;
    static const char * const _keywords[] = {"file", "mode", "locking", NULL};
    static _PyArg_Parser _parser = {"O|Op:FILE", _keywords, 0};
    PyObject *name_obj;
    const char *name;
    PyObject *mode_obj = Py_None;
    const char *mode;
    int locking = 0;
    FILE_DECLARES;
    
    if (!_PyArg_ParseTupleAndKeywordsFast(args, kwargs, &_parser,
                                          &name_obj, &mode_obj, &locking)) {
        goto exit;
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
    FILE *file = fopen(name, mode);
    FILE_EPILOG(self, file);
    if (file) {
      Py_BEGIN_ALLOW_THREADS
        __fsetlocking(locking ? FSETLOCKING_INTERNAL : FSETLOCKING_BYCALLER);
      Py_END_ALLOW_THREADS
    }
    PyObject_SetAttrString(self, "file", PyLong_FromLong((long)file));
    return NULL;

exit:
    return return_value;
}

PyObject *
FILE_fclose(PyObject *self)
{
  FILE_DECLARES;
  PyObject *file_obj = PyObject_GetAttrString(self, "file");
  if (file_obj == PyNone)
    Py_RETURN_NONE;
  FILE *file = PyLong_AsLong(file_obj);
  FILE_PROLOG(self, file);
  int result = fclose(file);
  FILE_EPILOG(self, 0);
  if (PyObject_SetAttrString(self, "file", PyNone))
    return NULL;
  Py_DECREF(file_obj);
  file_obj = PyNone;
  Py_INCREF(file_obj);
  return PyLong_FromLong(result);
}

PyObject *
FILE_fileno(PyObject *self)
{
  FILE_DECLARES;
  PyObject *file_obj = PyObject_GetAttrString(self, "file");
  if (file_obj == PyNone)
    Py_RETURN_NONE;
  FILE *file = PyLong_AsLong(file_obj);
  FILE_PROLOG(self, file);
  int result = fileno(file);
  FILE_EPILOG(self, file);
  return PyLong_FromLong(result);
}

PyObject *
FILE_fflush(PyObject *self) // METH_NOARGS
{
  FILE_DECLARES;
  PyObject *file_obj = PyObject_GetAttrString(self, "file");
  if (file_obj == PyNone)
    Py_RETURN_NONE;
  FILE *file = PyLong_AsLong(file_obj);
  FILE_PROLOG(self, file);
  int result = fflush(file);
  FILE_EPILOG(self, file);
  return PyLong_FromLong(result);
}

PyObject *
FILE_fread(PyObject *self, PyObject *args) // METH_VARARGS
{
  PyBuffer *buffer;
  FILE_DECLARES;
  PyObject *file_obj = PyObject_GetAttrString(self, "file");
  if (file_obj == PyNone)
    Py_RETURN_NONE;
  if (!PyArg_ParseTuple(args, "y*:fread", &buffer))
    return NULL;
  FILE *file = (FILE *)PyLong_AsLong(file_obj);
  FILE_PROLOG(self, file);
  int result = fread(buffer->buf, buffer->len, 1, file);
  FILE_EPILOG(self, file);
  PyBuffer_Release(buf);
  return PyLong_FromLong(result);
}

PyObject *
FILE_fwrite(PyObject *self, PyObject *args) // METH_VARARGS
{
  PyBuffer *buffer;
  FILE_DECLARES;
  PyObject *file_obj = PyObject_GetAttrString(self, "file");
  if (file_obj == PyNone)
    Py_RETURN_NONE;
  if (!PyArg_ParseTuple(args, "y*:fread", &buffer))
    return NULL;
  FILE *file = (FILE *)PyLong_AsLong(file_obj);
  FILE_PROLOG(self, file);
  int result = fwrite(buffer->buf, buffer->len, 1, file);
  FILE_EPILOG(self, file);
  PyBuffer_Release(buf);
  return PyLong_FromLong(result);
}

PyObject *
FILE_rewind(PyObject *self) // METH_NOARGS
{
  FILE_DECLARES;
  PyObject *file_obj = PyObject_GetAttrString(self, "file");
  if (file_obj == PyNone)
    Py_RETURN_NONE;
  FILE *file = PyLong_AsLong(file_obj);
  FILE_PROLOG(self, file);
  int result = rewind(file);
  FILE_EPILOG(self, file);
  return PyLong_FromLong(result);
}

PyObject *
FILE_fgetpos(PyObject *self) // METH_NOARGS
{
  PyObject *position = NULL;
  FILE_DECLARES;
  PyObject *file_obj = PyObject_GetAttrString(self, "file");
  if (file_obj == PyNone)
    Py_RETURN_NONE;
  if (PyObject_HasAttrString(self, "position"))
    position = PyObject_GetAttrString(self, "position");
  else {
    position = PyByteArray_FromStringAndSize(&position, sizeof(position));
    PyObject_SetAttrString(self, "position", position);
  }
  FILE *file = (FILE *)PyLong_AsLong(file_obj);
  FILE_PROLOG(self, file);
  int result = fgetpos(file, (fpos_t *)PyByteArray_AS_STRING(position));
  FILE_EPILOG(self, file);
  return PyLong_FromLong(result);
}

PyObject *
FILE_fsetpos(PyObject *self, PyObject *args) // METH_VARARGS
{
  PyObject *position = NULL;
  FILE_DECLARES;
  PyObject *file_obj = PyObject_GetAttrString(self, "file");
  if (file_obj == PyNone)
    Py_RETURN_NONE;
  if (!PyArg_ParseTuple(args, "y*:fread", &buffer))
    return NULL;
  if (PyObject_HasAttrString(self, "position"))
    position = PyObject_GetAttrString(self, "position");
  else {
    position = PyByteArray_FromStringAndSize(&position, sizeof(position));
    PyObject_SetAttrString(self, "position", position);
  }
  FILE *file = (FILE *)PyLong_AsLong(file_obj);
  FILE_PROLOG(self, file);
  int result = fsetpos(file, (fpos_t *)PyByteArray_AS_STRING(position));
  FILE_EPILOG(self, file);
  return PyLong_FromLong(result);
}

PyObject *
FILE_fldata(PyObject *self) // METH_NOARGS
{
  PyObject *position = NULL;
  fldata_t fldata_s;
  FILE_DECLARES;
  PyObject *file_obj = PyObject_GetAttrString(self, "file");
  if (file_obj == PyNone)
    Py_RETURN_NONE;
  if (PyObject_HasAttrString(self, "position"))
    position = PyObject_GetAttrString(self, "position");
  else {
    position = PyByteArray_FromStringAndSize(&position, sizeof(position));
    PyObject_SetAttrString(self, "position", position);
  }
  FILE *file = (FILE *)PyLong_AsLong(file_obj);
  FILE_PROLOG(self, file);
  int result = fldata(file, NULL, &fldata);
  FILE_EPILOG(self, file);
  return PyLong_FromLong(result);
}

/* int      __freadable (FILE *); */
/* int      __fwritable (FILE *); */

/* int    flocate (FILE *, const void *, size_t, int); */
/* int    fdelrec (FILE *); */
/* size_t fupdate (const void *, size_t, FILE *); */
/* int    clrmemf (int); */
/* int    fldata (FILE *, char *, fldata_t *); */

static PyObject *
path_error(path_t *path)
{
    return PyErr_SetFromErrnoWithFilenameObject(PyExc_OSError, path);
}

static PyObject *
zos_os_stat_internal(PyObject *module, PyObject *const *args, Py_ssize_t nargs, PyObject *kwnames)
{
    PyObject *return_value = NULL;
    static const char * const _keywords[] = {"path", "dir_fd", "follow_symlinks", NULL};
    static _PyArg_Parser _parser = {"O&|$O&p:stat", _keywords, 0};
    path_t path_s = PATH_T_INITIALIZE("stat", "path", 0, 1);
    path_t *path = &path_s;
    int dir_fd = DEFAULT_DIR_FD;
    int follow_symlinks = 1;

    if (!_PyArg_ParseStackAndKeywords(args, nargs, kwnames, &_parser,
        path_converter, path, dir_fd_unavailable, &dir_fd, &follow_symlinks)) {
        goto exit;
    }

    STRUCT_STAT st;
    int result;

    if (path_and_dir_fd_invalid("stat", path, dir_fd) ||
        dir_fd_and_fd_invalid("stat", dir_fd, path->fd) ||
        fd_and_follow_symlinks_invalid("stat", path->fd, follow_symlinks))
        return NULL;

    Py_BEGIN_ALLOW_THREADS
    if (path->fd != -1)
        result = fstat(path->fd, &st);
    else if ((!follow_symlinks) && (dir_fd == DEFAULT_DIR_FD))
        result = lstat(path->narrow, &st);
    else
        result = stat(path->narrow, &st);
    Py_END_ALLOW_THREADS

    if (result != 0) {
        return path_error(path);
    }

    return_value = PyBytes_FromStringAndSize(&st, sizeof(st));
exit:
    /* Cleanup for path */
    path_cleanup(&path);

    return return_value;
}

static PyObject *
zos_chattr_internal(PyObject *module, PyObject *const *args, Py_ssize_t nargs, PyObject *kwnames)
{
    PyObject *return_value = NULL;
    static const char * const _keywords[] = {"path", "dir_fd", "follow_symlinks", NULL};
    static _PyArg_Parser _parser = {"O&s#|$O&p:chattr", _keywords, 0};
    path_t path_s = PATH_T_INITIALIZE("chattr", "path", 0, 1);
    path_t *path = &path_s;
    int dir_fd = DEFAULT_DIR_FD;
    int follow_symlinks = 1;
    char *attributes;
    int attributes_len;

    if (!_PyArg_ParseStackAndKeywords(args, nargs, kwnames, &_parser,
                                      path_converter, path,
                                      &attributes, &attributes_len,
                                      dir_fd_unavailable, &dir_fd, &follow_symlinks)) {
        goto exit;
    }

    STRUCT_STAT st;
    int result;

    if (path_and_dir_fd_invalid("chattr", path, dir_fd) ||
        dir_fd_and_fd_invalid("chattr", dir_fd, path->fd) ||
        fd_and_follow_symlinks_invalid("chattr", path->fd, follow_symlinks))
        return NULL;

    Py_BEGIN_ALLOW_THREADS
    if (path->fd != -1)
        result = __fchattr(path->fd, (attrib_t *)attributes, attributes_len);
    else if ((!follow_symlinks) && (dir_fd == DEFAULT_DIR_FD))
      result = __lchattr(path->narrow, (attrib_t *)attributes, attributes_len);
    else
        result = __chattr(path->narrow, (attrib_t *)attributes, attributes_len);
    Py_END_ALLOW_THREADS

    if (result != 0) {
        return path_error(path);
    }

    Py_RETURN_NONE;
exit:
    /* Cleanup for path */
    path_cleanup(&path);

    return NULL;
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
  if (addr == NULL) {
    PyErr_SetString(PyExc_BufferError,
                    "Callot allocate");
    return NULL;
  }
  void *old_addr = self->ob_bytes;
  memcpy(new_addr, old_addr, self->ob_alloc);
  self->ob_bytes = new_addr;
  self->ob_start += (new_addr - old_addr);
  PyObject_Free(old_addr);
    
  memset(addr, 0, size);
  return addr;

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


#ifdef __MVS__
PyDoc_STRVAR(os_zos_system_call__doc__,
"B.zos_system_call() -> B\n\
\n\
");

/* r15, r0, r1, code_or_save, type */
#define SYSTEM_CALL__SVC    1
#define SYSTEM_CALL__PC     2
#define SYSTEM_CALL__CALL   3
#define SYSTEM_CALL__CALL31 4
       
static PyObject *
_zos_system_call(PyObject *self, PyObject *args)
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

  PyBuffer_Release(&buffer);
  Py_RETURN_NONE;
}


static PyMethodDef _zos_methods[] = {
  {"FILE___init__", FILE___init__, METH_FASTCALL | METH_KEYWORDS, doc},
  {"FILE_fclose", FILE_fclose, METH_NOARGS, doc};
  {"FILE_fileno", FILE_fileno, METH_NOARGS, doc};
  {"FILE_fflush", FILE_fflush, METH_NOARGS, doc};
  {"FILE_fread", FILE_fread,  METH_VARARGS, doc};
  {"FILE_fwrite", FILE_fwrite, METH_VARARGS, doc};
  {"FILE_rewind", FILE_rewind, METH_NOARGS, doc};
  {"FILE_fgetpos", FILE_fgetpos, METH_NOARGS, doc};
  {"FILE_fsetpos", FILE_fsetpos, METH_VARARGS, doc};
  {"FILE_fldata", FILE_fldata, METH_NOARGS, doc};
  {"stat_internal",   zos_stat_internal,  METH_FASTCALL|METH_KEYWORDS, zos_stat_internal__doc__},
  {"chattr_internal", zos_chattr_internal,METH_VARARGS, zos_chattr_internal__doc__},
  {"system_call", os_zos_system_call, METH_VARARGS, zos_system_call__doc__},
  {"bytearray_set_address_size", (PyCFunction)bytearray_set_address_size, METH_O, bytearray_set_addresss_size__doc__},
  {"bytearray_buffer_address", (PyCFunction)bytearray_buffer_address, METH_NOARGS, bytearray_buffer_address__doc__},
  {NULL,              NULL}            /* Sentinel */
}

static struct PyModuleDef _zosmodule = {
    PyModuleDef_HEAD_INIT,
    MODNAME,
    _zos__doc__,
    -1,
    _zos_methods,
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

    m = PyModule_Create(&_zosmodule);
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
#ifdef __MVS__
    if (PyModule_AddIntMacro(m, SYSTEM_CALL__SVC)) return NULL;
    if (PyModule_AddIntMacro(m, SYSTEM_CALL__PC)) return NULL;
    if (PyModule_AddIntMacro(m, SYSTEM_CALL__CALL)) return NULL;
    if (PyModule_AddIntMacro(m, SYSTEM_CALL__CALL31)) return NULL;
#endif

    return m;
}
