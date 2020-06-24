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

typedef struct {
    const char *function_name;
    const char *argument_name;
    int nullable;
    int allow_fd;
    const wchar_t *wide;
    const char *narrow;
    int fd;
    Py_ssize_t length;
    PyObject *object;
    PyObject *cleanup;
} path_t;

#define PATH_T_INITIALIZE(function_name, argument_name, nullable, allow_fd) \
    {function_name, argument_name, nullable, allow_fd, NULL, NULL, -1, 0, NULL, NULL}

static void
path_cleanup(path_t *path)
{
    Py_CLEAR(path->object);
    Py_CLEAR(path->cleanup);
}

static int
path_converter(PyObject *o, void *p)
{
    path_t *path = (path_t *)p;
    PyObject *bytes = NULL;
    Py_ssize_t length = 0;
    int is_index, is_buffer, is_bytes, is_unicode;
    const char *narrow;
#ifdef MS_WINDOWS
    PyObject *wo = NULL;
    const wchar_t *wide;
#endif

#define FORMAT_EXCEPTION(exc, fmt) \
    PyErr_Format(exc, "%s%s" fmt, \
        path->function_name ? path->function_name : "", \
        path->function_name ? ": "                : "", \
        path->argument_name ? path->argument_name : "path")

    /* Py_CLEANUP_SUPPORTED support */
    if (o == NULL) {
        path_cleanup(path);
        return 1;
    }

    /* Ensure it's always safe to call path_cleanup(). */
    path->object = path->cleanup = NULL;
    /* path->object owns a reference to the original object */
    Py_INCREF(o);

    if ((o == Py_None) && path->nullable) {
        path->wide = NULL;
#ifdef MS_WINDOWS
        path->narrow = FALSE;
#else
        path->narrow = NULL;
#endif
        path->fd = -1;
        goto success_exit;
    }

    /* Only call this here so that we don't treat the return value of
       os.fspath() as an fd or buffer. */
    is_index = path->allow_fd && PyIndex_Check(o);
    is_buffer = PyObject_CheckBuffer(o);
    is_bytes = PyBytes_Check(o);
    is_unicode = PyUnicode_Check(o);

    if (!is_index && !is_buffer && !is_unicode && !is_bytes) {
        /* Inline PyOS_FSPath() for better error messages. */
        _Py_IDENTIFIER(__fspath__);
        PyObject *func, *res;

        func = _PyObject_LookupSpecial(o, &PyId___fspath__);
        if (NULL == func) {
            goto error_format;
        }
        res = _PyObject_CallNoArg(func);
        Py_DECREF(func);
        if (NULL == res) {
            goto error_exit;
        }
        else if (PyUnicode_Check(res)) {
            is_unicode = 1;
        }
        else if (PyBytes_Check(res)) {
            is_bytes = 1;
        }
        else {
            PyErr_Format(PyExc_TypeError,
                 "expected %.200s.__fspath__() to return str or bytes, "
                 "not %.200s", Py_TYPE(o)->tp_name,
                 Py_TYPE(res)->tp_name);
            Py_DECREF(res);
            goto error_exit;
        }

        /* still owns a reference to the original object */
        Py_DECREF(o);
        o = res;
    }

    if (is_unicode) {
#ifdef MS_WINDOWS
        wide = PyUnicode_AsUnicodeAndSize(o, &length);
        if (!wide) {
            goto error_exit;
        }
        if (length > 32767) {
            FORMAT_EXCEPTION(PyExc_ValueError, "%s too long for Windows");
            goto error_exit;
        }
        if (wcslen(wide) != length) {
            FORMAT_EXCEPTION(PyExc_ValueError, "embedded null character in %s");
            goto error_exit;
        }

        path->wide = wide;
        path->narrow = FALSE;
        path->fd = -1;
        goto success_exit;
#else
        if (!PyUnicode_FSConverter(o, &bytes)) {
            goto error_exit;
        }
#endif
    }
    else if (is_bytes) {
        bytes = o;
        Py_INCREF(bytes);
    }
    else if (is_buffer) {
        /* XXX Replace PyObject_CheckBuffer with PyBytes_Check in other code
           after removing support of non-bytes buffer objects. */
        if (PyErr_WarnFormat(PyExc_DeprecationWarning, 1,
            "%s%s%s should be %s, not %.200s",
            path->function_name ? path->function_name : "",
            path->function_name ? ": "                : "",
            path->argument_name ? path->argument_name : "path",
            path->allow_fd && path->nullable ? "string, bytes, os.PathLike, "
                                               "integer or None" :
            path->allow_fd ? "string, bytes, os.PathLike or integer" :
            path->nullable ? "string, bytes, os.PathLike or None" :
                             "string, bytes or os.PathLike",
            Py_TYPE(o)->tp_name)) {
            goto error_exit;
        }
        bytes = PyBytes_FromObject(o);
        if (!bytes) {
            goto error_exit;
        }
    }
    else if (is_index) {
        if (!_fd_converter(o, &path->fd)) {
            goto error_exit;
        }
        path->wide = NULL;
#ifdef MS_WINDOWS
        path->narrow = FALSE;
#else
        path->narrow = NULL;
#endif
        goto success_exit;
    }
    else {
 error_format:
        PyErr_Format(PyExc_TypeError, "%s%s%s should be %s, not %.200s",
            path->function_name ? path->function_name : "",
            path->function_name ? ": "                : "",
            path->argument_name ? path->argument_name : "path",
            path->allow_fd && path->nullable ? "string, bytes, os.PathLike, "
                                               "integer or None" :
            path->allow_fd ? "string, bytes, os.PathLike or integer" :
            path->nullable ? "string, bytes, os.PathLike or None" :
                             "string, bytes or os.PathLike",
            Py_TYPE(o)->tp_name);
        goto error_exit;
    }

    length = PyBytes_GET_SIZE(bytes);
    narrow = PyBytes_AS_STRING(bytes);
    if ((size_t)length != strlen(narrow)) {
        FORMAT_EXCEPTION(PyExc_ValueError, "embedded null character in %s");
        goto error_exit;
    }

#ifdef MS_WINDOWS
    wo = PyUnicode_DecodeFSDefaultAndSize(
        narrow,
        length
    );
    if (!wo) {
        goto error_exit;
    }

    wide = PyUnicode_AsUnicodeAndSize(wo, &length);
    if (!wide) {
        goto error_exit;
    }
    if (length > 32767) {
        FORMAT_EXCEPTION(PyExc_ValueError, "%s too long for Windows");
        goto error_exit;
    }
    if (wcslen(wide) != length) {
        FORMAT_EXCEPTION(PyExc_ValueError, "embedded null character in %s");
        goto error_exit;
    }
    path->wide = wide;
    path->narrow = TRUE;
    path->cleanup = wo;
    Py_DECREF(bytes);
#else
    path->wide = NULL;
    path->narrow = narrow;
    if (bytes == o) {
        /* Still a reference owned by path->object, don't have to
           worry about path->narrow is used after free. */
        Py_DECREF(bytes);
    }
    else {
        path->cleanup = bytes;
    }
#endif
    path->fd = -1;

 success_exit:
    path->length = length;
    path->object = o;
    return Py_CLEANUP_SUPPORTED;

 error_exit:
    Py_XDECREF(o);
    Py_XDECREF(bytes);
#ifdef MS_WINDOWS
    Py_XDECREF(wo);
#endif
    return 0;
}

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

  Py_buffer_Release(&buffer);
  Py_RETURN_NONE;
}

static char *doc = "";

static PyMethodDef _zos_methods[] = {
  {"stat_internal",   zos_stat_internal,  METH_FASTCALL|METH_KEYWORDS, zos_stat_internal__doc__},
  {"chattr_internal", zos_chattr_internal,METH_VARARGS, zos_chattr_internal__doc__},
  {"system_call", os_zos_system_call, METH_VARARGS, zos_system_call__doc__},
  {"bytearray_set_address_size", (PyCFunction)bytearray_set_address_size, METH_O, bytearray_set_addresss_size__doc__},
  {"bytearray_buffer_address", (PyCFunction)bytearray_buffer_address, METH_NOARGS, bytearray_buffer_address__doc__},
  {NULL,              NULL}            /* Sentinel */
};

static char *_zos__doc__="";

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

#ifdef __MVS__
    if (PyModule_AddIntMacro(m, SYSTEM_CALL__SVC)) return NULL;
    if (PyModule_AddIntMacro(m, SYSTEM_CALL__PC)) return NULL;
    if (PyModule_AddIntMacro(m, SYSTEM_CALL__CALL)) return NULL;
    if (PyModule_AddIntMacro(m, SYSTEM_CALL__CALL31)) return NULL;
#endif

    return m;
}
