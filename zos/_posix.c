
/* POSIX module implementation */

/* This file is also used for Windows NT/MS-Win.  In that case the
   module actually calls itself 'nt', not 'posix', and a few
   functions are either unimplemented or implemented differently.  The source
   assumes that for Windows NT, the macro 'MS_WINDOWS' is defined independent
   of the compiler used.  Different compilers define their own feature
   test macro, e.g. '_MSC_VER'. */



#ifdef __APPLE__
   /*
    * Step 1 of support for weak-linking a number of symbols existing on
    * OSX 10.4 and later, see the comment in the #ifdef __APPLE__ block
    * at the end of this file for more information.
    */
#  pragma weak lchown
#  pragma weak statvfs
#  pragma weak fstatvfs

#endif /* __APPLE__ */

#ifdef __MVS__
#define _OPEN_SYS_FILE_EXT 1
#define HAVE_SPAWNV 1
#endif

#define PY_SSIZE_T_CLEAN

#include "Python.h"
#ifdef MS_WINDOWS
   /* include <windows.h> early to avoid conflict with pycore_condvar.h:

        #define WIN32_LEAN_AND_MEAN
        #include <windows.h>

      FSCTL_GET_REPARSE_POINT is not exported with WIN32_LEAN_AND_MEAN. */
#  include <windows.h>
#endif

#include "pycore_ceval.h"     /* _PyEval_ReInitThreads() */
#include "pycore_pystate.h"   /* _PyRuntime */
#include "pythread.h"
#include "structmember.h"
#ifndef MS_WINDOWS
#  include "posixmodule.h"
#else
#  include "winreparse.h"
#endif

/* On android API level 21, 'AT_EACCESS' is not declared although
 * HAVE_FACCESSAT is defined. */
#ifdef __ANDROID__
#undef HAVE_FACCESSAT
#endif

#include <stdio.h>  /* needed for ctermid() */

#ifdef __MVS__
#include <encode_standard_files.h>
#include <semaphore.h>
#define NSIG 256
#endif

#ifdef __MVS__
#include <_Ieee754.h>
#endif

#ifdef __cplusplus
extern "C" {
#endif

PyDoc_STRVAR(posix__doc__,
"This module provides access to operating system functionality that is\n\
standardized by the C Standard and the POSIX standard (a thinly\n\
disguised Unix interface).  Refer to the library manual and\n\
corresponding Unix manual entries for more information on calls.");


#ifdef HAVE_SYS_UIO_H
#include <sys/uio.h>
#endif

#ifdef HAVE_SYS_SYSMACROS_H
/* GNU C Library: major(), minor(), makedev() */
#include <sys/sysmacros.h>
#endif

#ifdef HAVE_SYS_TYPES_H
#include <sys/types.h>
#endif /* HAVE_SYS_TYPES_H */

#ifdef HAVE_SYS_STAT_H
#include <sys/stat.h>
#endif /* HAVE_SYS_STAT_H */

#ifdef HAVE_SYS_MODES_H
#include <sys/modes.h>
#endif /* HAVE_SYS_MODES_H */

#ifdef HAVE_SYS_WAIT_H
#include <sys/wait.h>           /* For WNOHANG */
#endif

#ifdef HAVE_SIGNAL_H
#include <signal.h>
#endif

#ifdef HAVE_FCNTL_H
#include <fcntl.h>
#endif /* HAVE_FCNTL_H */

#ifdef HAVE_GRP_H
#include <grp.h>
#endif

#ifdef HAVE_SYSEXITS_H
#include <sysexits.h>
#endif /* HAVE_SYSEXITS_H */

#ifdef HAVE_SYS_LOADAVG_H
#include <sys/loadavg.h>
#endif

#ifdef HAVE_SYS_SENDFILE_H
#include <sys/sendfile.h>
#endif

#if defined(__APPLE__)
#include <copyfile.h>
#endif

#ifdef HAVE_SCHED_H
#include <sched.h>
#endif

#ifdef HAVE_COPY_FILE_RANGE
#include <unistd.h>
#endif

#if !defined(CPU_ALLOC) && defined(HAVE_SCHED_SETAFFINITY)
#undef HAVE_SCHED_SETAFFINITY
#endif

#if defined(HAVE_SYS_XATTR_H) && defined(__GLIBC__) && !defined(__FreeBSD_kernel__) && !defined(__GNU__)
#define USE_XATTRS
#endif

#ifdef USE_XATTRS
#include <sys/xattr.h>
#endif

#if defined(__FreeBSD__) || defined(__DragonFly__) || defined(__APPLE__)
#ifdef HAVE_SYS_SOCKET_H
#include <sys/socket.h>
#endif
#endif

#ifdef HAVE_DLFCN_H
#include <dlfcn.h>
#endif

#ifdef __hpux
#include <sys/mpctl.h>
#endif

#if defined(__DragonFly__) || \
    defined(__OpenBSD__)   || \
    defined(__FreeBSD__)   || \
    defined(__NetBSD__)    || \
    defined(__APPLE__)
#include <sys/sysctl.h>
#endif

#ifdef HAVE_LINUX_RANDOM_H
#  include <linux/random.h>
#endif
#ifdef HAVE_GETRANDOM_SYSCALL
#  include <sys/syscall.h>
#endif

#if defined(MS_WINDOWS)
#  define TERMSIZE_USE_CONIO
#elif defined(HAVE_SYS_IOCTL_H)
#  include <sys/ioctl.h>
#  if defined(HAVE_TERMIOS_H)
#    include <termios.h>
#  endif
#  if defined(TIOCGWINSZ)
#    define TERMSIZE_USE_IOCTL
#  endif
#endif /* MS_WINDOWS */

/* Various compilers have only certain posix functions */
/* XXX Gosh I wish these were all moved into pyconfig.h */
#if defined(__WATCOMC__) && !defined(__QNX__)           /* Watcom compiler */
#define HAVE_OPENDIR    1
#define HAVE_SYSTEM     1
#include <process.h>
#else
#ifdef _MSC_VER         /* Microsoft compiler */
#define HAVE_GETPPID    1
#define HAVE_GETLOGIN   1
#define HAVE_SPAWNV     1
#define HAVE_EXECV      1
#define HAVE_WSPAWNV    1
#define HAVE_WEXECV     1
#define HAVE_PIPE       1
#define HAVE_SYSTEM     1
#define HAVE_CWAIT      1
#define HAVE_FSYNC      1
#define fsync _commit
#else
/* Unix functions that the configure script doesn't check for */
#ifndef __VXWORKS__
#define HAVE_EXECV      1
#define HAVE_FORK       1
#if defined(__USLC__) && defined(__SCO_VERSION__)       /* SCO UDK Compiler */
#define HAVE_FORK1      1
#endif
#endif
#define HAVE_GETEGID    1
#define HAVE_GETEUID    1
#define HAVE_GETGID     1
#define HAVE_GETPPID    1
#define HAVE_GETUID     1
#define HAVE_KILL       1
#define HAVE_OPENDIR    1
#define HAVE_PIPE       1
#define HAVE_SYSTEM     1
#define HAVE_WAIT       1
#define HAVE_TTYNAME    1
#endif  /* _MSC_VER */
#endif  /* ! __WATCOMC__ || __QNX__ */


/*[clinic input]
# one of the few times we lie about this name!
module os
[clinic start generated code]*/
/*[clinic end generated code: output=da39a3ee5e6b4b0d input=94a0f0f978acae17]*/

#ifndef _MSC_VER

#if defined(__sgi)&&_COMPILER_VERSION>=700
/* declare ctermid_r if compiling with MIPSPro 7.x in ANSI C mode
   (default) */
extern char        *ctermid_r(char *);
#endif

#endif /* !_MSC_VER */

#if defined(__VXWORKS__)
#include <vxCpuLib.h>
#include <rtpLib.h>
#include <wait.h>
#include <taskLib.h>
#ifndef _P_WAIT
#define _P_WAIT          0
#define _P_NOWAIT        1
#define _P_NOWAITO       1
#endif
#endif /* __VXWORKS__ */

#ifdef HAVE_POSIX_SPAWN
#include <spawn.h>
#endif

#ifdef HAVE_UTIME_H
#include <utime.h>
#endif /* HAVE_UTIME_H */

#ifdef HAVE_SYS_UTIME_H
#include <sys/utime.h>
#define HAVE_UTIME_H /* pretend we do for the rest of this file */
#endif /* HAVE_SYS_UTIME_H */

#ifdef HAVE_SYS_TIMES_H
#include <sys/times.h>
#endif /* HAVE_SYS_TIMES_H */

#ifdef HAVE_SYS_PARAM_H
#include <sys/param.h>
#endif /* HAVE_SYS_PARAM_H */

#ifdef HAVE_SYS_UTSNAME_H
#include <sys/utsname.h>
#endif /* HAVE_SYS_UTSNAME_H */

#ifdef HAVE_DIRENT_H
#include <dirent.h>
#define NAMLEN(dirent) strlen((dirent)->d_name)
#else
#if defined(__WATCOMC__) && !defined(__QNX__)
#include <direct.h>
#define NAMLEN(dirent) strlen((dirent)->d_name)
#else
#define dirent direct
#define NAMLEN(dirent) (dirent)->d_namlen
#endif
#ifdef HAVE_SYS_NDIR_H
#include <sys/ndir.h>
#endif
#ifdef HAVE_SYS_DIR_H
#include <sys/dir.h>
#endif
#ifdef HAVE_NDIR_H
#include <ndir.h>
#endif
#endif

#ifdef _MSC_VER
#ifdef HAVE_DIRECT_H
#include <direct.h>
#endif
#ifdef HAVE_IO_H
#include <io.h>
#endif
#ifdef HAVE_PROCESS_H
#include <process.h>
#endif
#ifndef IO_REPARSE_TAG_SYMLINK
#define IO_REPARSE_TAG_SYMLINK (0xA000000CL)
#endif
#ifndef IO_REPARSE_TAG_MOUNT_POINT
#define IO_REPARSE_TAG_MOUNT_POINT (0xA0000003L)
#endif
#include "osdefs.h"
#include <malloc.h>
#include <windows.h>
#include <shellapi.h>   /* for ShellExecute() */
#include <lmcons.h>     /* for UNLEN */
#define HAVE_SYMLINK
#endif /* _MSC_VER */

#ifndef MAXPATHLEN
#if defined(PATH_MAX) && PATH_MAX > 1024
#define MAXPATHLEN PATH_MAX
#else
#define MAXPATHLEN 1024
#endif
#endif /* MAXPATHLEN */

#ifdef UNION_WAIT
/* Emulate some macros on systems that have a union instead of macros */

#ifndef WIFEXITED
#define WIFEXITED(u_wait) (!(u_wait).w_termsig && !(u_wait).w_coredump)
#endif

#ifndef WEXITSTATUS
#define WEXITSTATUS(u_wait) (WIFEXITED(u_wait)?((u_wait).w_retcode):-1)
#endif

#ifndef WTERMSIG
#define WTERMSIG(u_wait) ((u_wait).w_termsig)
#endif

#define WAIT_TYPE union wait
#define WAIT_STATUS_INT(s) (s.w_status)

#else /* !UNION_WAIT */
#define WAIT_TYPE int
#define WAIT_STATUS_INT(s) (s)
#endif /* UNION_WAIT */

/* Don't use the "_r" form if we don't need it (also, won't have a
   prototype for it, at least on Solaris -- maybe others as well?). */
#if defined(HAVE_CTERMID_R)
#define USE_CTERMID_R
#endif

/* choose the appropriate stat and fstat functions and return structs */
#undef STAT
#undef FSTAT
#undef STRUCT_STAT
#ifdef MS_WINDOWS
#       define STAT win32_stat
#       define LSTAT win32_lstat
#       define FSTAT _Py_fstat_noraise
#       define STRUCT_STAT struct _Py_stat_struct
#else
#       define STAT stat
#       define LSTAT lstat
#       define FSTAT fstat
#       define STRUCT_STAT struct stat
#endif

#if defined(MAJOR_IN_MKDEV)
#include <sys/mkdev.h>
#else
#if defined(MAJOR_IN_SYSMACROS)
#include <sys/sysmacros.h>
#endif
#if defined(HAVE_MKNOD) && defined(HAVE_SYS_MKDEV_H)
#include <sys/mkdev.h>
#endif
#endif

#if defined(__sun)
/* Something to implement in autoconf, not present in autoconf 2.69 */
#define HAVE_STRUCT_STAT_ST_FSTYPE 1
#endif

/* memfd_create is either defined in sys/mman.h or sys/memfd.h
 * linux/memfd.h defines additional flags
 */
#ifdef HAVE_SYS_MMAN_H
#include <sys/mman.h>
#endif
#ifdef HAVE_SYS_MEMFD_H
#include <sys/memfd.h>
#endif
#ifdef HAVE_LINUX_MEMFD_H
#include <linux/memfd.h>
#endif

#ifdef _Py_MEMORY_SANITIZER
# include <sanitizer/msan_interface.h>
#endif



#ifdef MS_WINDOWS
/* defined in fileutils.c */
void _Py_time_t_to_FILE_TIME(time_t, int, FILETIME *);
void _Py_attribute_data_to_stat(BY_HANDLE_FILE_INFORMATION *,
                                            ULONG, struct _Py_stat_struct *);
#endif


#ifndef MS_WINDOWS
PyObject *
_PyLong_FromUid(uid_t uid)
{
    if (uid == (uid_t)-1)
        return PyLong_FromLong(-1);
    return PyLong_FromUnsignedLong(uid);
}

PyObject *
_PyLong_FromGid(gid_t gid)
{
    if (gid == (gid_t)-1)
        return PyLong_FromLong(-1);
    return PyLong_FromUnsignedLong(gid);
}

int
_Py_Uid_Converter(PyObject *obj, void *p)
{
    uid_t uid;
    PyObject *index;
    int overflow;
    long result;
    unsigned long uresult;

    index = PyNumber_Index(obj);
    if (index == NULL) {
        PyErr_Format(PyExc_TypeError,
                     "uid should be integer, not %.200s",
                     Py_TYPE(obj)->tp_name);
        return 0;
    }

    /*
     * Handling uid_t is complicated for two reasons:
     *  * Although uid_t is (always?) unsigned, it still
     *    accepts -1.
     *  * We don't know its size in advance--it may be
     *    bigger than an int, or it may be smaller than
     *    a long.
     *
     * So a bit of defensive programming is in order.
     * Start with interpreting the value passed
     * in as a signed long and see if it works.
     */

    result = PyLong_AsLongAndOverflow(index, &overflow);

    if (!overflow) {
        uid = (uid_t)result;

        if (result == -1) {
            if (PyErr_Occurred())
                goto fail;
            /* It's a legitimate -1, we're done. */
            goto success;
        }

        /* Any other negative number is disallowed. */
        if (result < 0)
            goto underflow;

        /* Ensure the value wasn't truncated. */
        if (sizeof(uid_t) < sizeof(long) &&
            (long)uid != result)
            goto underflow;
        goto success;
    }

    if (overflow < 0)
        goto underflow;

    /*
     * Okay, the value overflowed a signed long.  If it
     * fits in an *unsigned* long, it may still be okay,
     * as uid_t may be unsigned long on this platform.
     */
    uresult = PyLong_AsUnsignedLong(index);
    if (PyErr_Occurred()) {
        if (PyErr_ExceptionMatches(PyExc_OverflowError))
            goto overflow;
        goto fail;
    }

    uid = (uid_t)uresult;

    /*
     * If uid == (uid_t)-1, the user actually passed in ULONG_MAX,
     * but this value would get interpreted as (uid_t)-1  by chown
     * and its siblings.   That's not what the user meant!  So we
     * throw an overflow exception instead.   (We already
     * handled a real -1 with PyLong_AsLongAndOverflow() above.)
     */
    if (uid == (uid_t)-1)
        goto overflow;

    /* Ensure the value wasn't truncated. */
    if (sizeof(uid_t) < sizeof(long) &&
        (unsigned long)uid != uresult)
        goto overflow;
    /* fallthrough */

success:
    Py_DECREF(index);
    *(uid_t *)p = uid;
    return 1;

underflow:
    PyErr_SetString(PyExc_OverflowError,
                    "uid is less than minimum");
    goto fail;

overflow:
    PyErr_SetString(PyExc_OverflowError,
                    "uid is greater than maximum");
    /* fallthrough */

fail:
    Py_DECREF(index);
    return 0;
}

int
_Py_Gid_Converter(PyObject *obj, void *p)
{
    gid_t gid;
    PyObject *index;
    int overflow;
    long result;
    unsigned long uresult;

    index = PyNumber_Index(obj);
    if (index == NULL) {
        PyErr_Format(PyExc_TypeError,
                     "gid should be integer, not %.200s",
                     Py_TYPE(obj)->tp_name);
        return 0;
    }

    /*
     * Handling gid_t is complicated for two reasons:
     *  * Although gid_t is (always?) unsigned, it still
     *    accepts -1.
     *  * We don't know its size in advance--it may be
     *    bigger than an int, or it may be smaller than
     *    a long.
     *
     * So a bit of defensive programming is in order.
     * Start with interpreting the value passed
     * in as a signed long and see if it works.
     */

    result = PyLong_AsLongAndOverflow(index, &overflow);

    if (!overflow) {
        gid = (gid_t)result;

        if (result == -1) {
            if (PyErr_Occurred())
                goto fail;
            /* It's a legitimate -1, we're done. */
            goto success;
        }

        /* Any other negative number is disallowed. */
        if (result < 0) {
            goto underflow;
        }

        /* Ensure the value wasn't truncated. */
        if (sizeof(gid_t) < sizeof(long) &&
            (long)gid != result)
            goto underflow;
        goto success;
    }

    if (overflow < 0)
        goto underflow;

    /*
     * Okay, the value overflowed a signed long.  If it
     * fits in an *unsigned* long, it may still be okay,
     * as gid_t may be unsigned long on this platform.
     */
    uresult = PyLong_AsUnsignedLong(index);
    if (PyErr_Occurred()) {
        if (PyErr_ExceptionMatches(PyExc_OverflowError))
            goto overflow;
        goto fail;
    }

    gid = (gid_t)uresult;

    /*
     * If gid == (gid_t)-1, the user actually passed in ULONG_MAX,
     * but this value would get interpreted as (gid_t)-1  by chown
     * and its siblings.   That's not what the user meant!  So we
     * throw an overflow exception instead.   (We already
     * handled a real -1 with PyLong_AsLongAndOverflow() above.)
     */
    if (gid == (gid_t)-1)
        goto overflow;

    /* Ensure the value wasn't truncated. */
    if (sizeof(gid_t) < sizeof(long) &&
        (unsigned long)gid != uresult)
        goto overflow;
    /* fallthrough */

success:
    Py_DECREF(index);
    *(gid_t *)p = gid;
    return 1;

underflow:
    PyErr_SetString(PyExc_OverflowError,
                    "gid is less than minimum");
    goto fail;

overflow:
    PyErr_SetString(PyExc_OverflowError,
                    "gid is greater than maximum");
    /* fallthrough */

fail:
    Py_DECREF(index);
    return 0;
}
#endif /* MS_WINDOWS */


#define _PyLong_FromDev PyLong_FromLongLong


#if defined(HAVE_MKNOD) && defined(HAVE_MAKEDEV)
static int
_Py_Dev_Converter(PyObject *obj, void *p)
{
    *((dev_t *)p) = PyLong_AsUnsignedLongLong(obj);
    if (PyErr_Occurred())
        return 0;
    return 1;
}
#endif /* HAVE_MKNOD && HAVE_MAKEDEV */


#ifdef AT_FDCWD
/*
 * Why the (int) cast?  Solaris 10 defines AT_FDCWD as 0xffd19553 (-3041965);
 * without the int cast, the value gets interpreted as uint (4291925331),
 * which doesn't play nicely with all the initializer lines in this file that
 * look like this:
 *      int dir_fd = DEFAULT_DIR_FD;
 */
#define DEFAULT_DIR_FD (int)AT_FDCWD
#else
#define DEFAULT_DIR_FD (-100)
#endif

static int
_fd_converter(PyObject *o, int *p)
{
    int overflow;
    long long_value;

    PyObject *index = PyNumber_Index(o);
    if (index == NULL) {
        return 0;
    }

    assert(PyLong_Check(index));
    long_value = PyLong_AsLongAndOverflow(index, &overflow);
    Py_DECREF(index);
    assert(!PyErr_Occurred());
    if (overflow > 0 || long_value > INT_MAX) {
        PyErr_SetString(PyExc_OverflowError,
                        "fd is greater than maximum");
        return 0;
    }
    if (overflow < 0 || long_value < INT_MIN) {
        PyErr_SetString(PyExc_OverflowError,
                        "fd is less than minimum");
        return 0;
    }

    *p = (int)long_value;
    return 1;
}

static int
dir_fd_converter(PyObject *o, void *p)
{
    if (o == Py_None) {
        *(int *)p = DEFAULT_DIR_FD;
        return 1;
    }
    else if (PyIndex_Check(o)) {
        return _fd_converter(o, (int *)p);
    }
    else {
        PyErr_Format(PyExc_TypeError,
                     "argument should be integer or None, not %.200s",
                     Py_TYPE(o)->tp_name);
        return 0;
    }
}


/*
 * A PyArg_ParseTuple "converter" function
 * that handles filesystem paths in the manner
 * preferred by the os module.
 *
 * path_converter accepts (Unicode) strings and their
 * subclasses, and bytes and their subclasses.  What
 * it does with the argument depends on the platform:
 *
 *   * On Windows, if we get a (Unicode) string we
 *     extract the wchar_t * and return it; if we get
 *     bytes we decode to wchar_t * and return that.
 *
 *   * On all other platforms, strings are encoded
 *     to bytes using PyUnicode_FSConverter, then we
 *     extract the char * from the bytes object and
 *     return that.
 *
 * path_converter also optionally accepts signed
 * integers (representing open file descriptors) instead
 * of path strings.
 *
 * Input fields:
 *   path.nullable
 *     If nonzero, the path is permitted to be None.
 *   path.allow_fd
 *     If nonzero, the path is permitted to be a file handle
 *     (a signed int) instead of a string.
 *   path.function_name
 *     If non-NULL, path_converter will use that as the name
 *     of the function in error messages.
 *     (If path.function_name is NULL it omits the function name.)
 *   path.argument_name
 *     If non-NULL, path_converter will use that as the name
 *     of the parameter in error messages.
 *     (If path.argument_name is NULL it uses "path".)
 *
 * Output fields:
 *   path.wide
 *     Points to the path if it was expressed as Unicode
 *     and was not encoded.  (Only used on Windows.)
 *   path.narrow
 *     Points to the path if it was expressed as bytes,
 *     or it was Unicode and was encoded to bytes. (On Windows,
 *     is a non-zero integer if the path was expressed as bytes.
 *     The type is deliberately incompatible to prevent misuse.)
 *   path.fd
 *     Contains a file descriptor if path.accept_fd was true
 *     and the caller provided a signed integer instead of any
 *     sort of string.
 *
 *     WARNING: if your "path" parameter is optional, and is
 *     unspecified, path_converter will never get called.
 *     So if you set allow_fd, you *MUST* initialize path.fd = -1
 *     yourself!
 *   path.length
 *     The length of the path in characters, if specified as
 *     a string.
 *   path.object
 *     The original object passed in (if get a PathLike object,
 *     the result of PyOS_FSPath() is treated as the original object).
 *     Own a reference to the object.
 *   path.cleanup
 *     For internal use only.  May point to a temporary object.
 *     (Pay no attention to the man behind the curtain.)
 *
 *   At most one of path.wide or path.narrow will be non-NULL.
 *   If path was None and path.nullable was set,
 *     or if path was an integer and path.allow_fd was set,
 *     both path.wide and path.narrow will be NULL
 *     and path.length will be 0.
 *
 *   path_converter takes care to not write to the path_t
 *   unless it's successful.  However it must reset the
 *   "cleanup" field each time it's called.
 *
 * Use as follows:
 *      path_t path;
 *      memset(&path, 0, sizeof(path));
 *      PyArg_ParseTuple(args, "O&", path_converter, &path);
 *      // ... use values from path ...
 *      path_cleanup(&path);
 *
 * (Note that if PyArg_Parse fails you don't need to call
 * path_cleanup().  However it is safe to do so.)
 */
typedef struct {
    const char *function_name;
    const char *argument_name;
    int nullable;
    int allow_fd;
    const wchar_t *wide;
#ifdef MS_WINDOWS
    BOOL narrow;
#else
    const char *narrow;
#endif
    int fd;
    Py_ssize_t length;
    PyObject *object;
    PyObject *cleanup;
} path_t;

#ifdef MS_WINDOWS
#define PATH_T_INITIALIZE(function_name, argument_name, nullable, allow_fd) \
    {function_name, argument_name, nullable, allow_fd, NULL, FALSE, -1, 0, NULL, NULL}
#else
#define PATH_T_INITIALIZE(function_name, argument_name, nullable, allow_fd) \
    {function_name, argument_name, nullable, allow_fd, NULL, NULL, -1, 0, NULL, NULL}
#endif

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

static void
argument_unavailable_error(const char *function_name, const char *argument_name)
{
    PyErr_Format(PyExc_NotImplementedError,
        "%s%s%s unavailable on this platform",
        (function_name != NULL) ? function_name : "",
        (function_name != NULL) ? ": ": "",
        argument_name);
}

static int
dir_fd_unavailable(PyObject *o, void *p)
{
    int dir_fd;
    if (!dir_fd_converter(o, &dir_fd))
        return 0;
    if (dir_fd != DEFAULT_DIR_FD) {
        argument_unavailable_error(NULL, "dir_fd");
        return 0;
    }
    *(int *)p = dir_fd;
    return 1;
}

static int
fd_specified(const char *function_name, int fd)
{
    if (fd == -1)
        return 0;

    argument_unavailable_error(function_name, "fd");
    return 1;
}

static int
follow_symlinks_specified(const char *function_name, int follow_symlinks)
{
    if (follow_symlinks)
        return 0;

    argument_unavailable_error(function_name, "follow_symlinks");
    return 1;
}

static int
path_and_dir_fd_invalid(const char *function_name, path_t *path, int dir_fd)
{
    if (!path->wide && (dir_fd != DEFAULT_DIR_FD)
#ifndef MS_WINDOWS
        && !path->narrow
#endif
    ) {
        PyErr_Format(PyExc_ValueError,
                     "%s: can't specify dir_fd without matching path",
                     function_name);
        return 1;
    }
    return 0;
}

static int
dir_fd_and_fd_invalid(const char *function_name, int dir_fd, int fd)
{
    if ((dir_fd != DEFAULT_DIR_FD) && (fd != -1)) {
        PyErr_Format(PyExc_ValueError,
                     "%s: can't specify both dir_fd and fd",
                     function_name);
        return 1;
    }
    return 0;
}

static int
fd_and_follow_symlinks_invalid(const char *function_name, int fd,
                               int follow_symlinks)
{
    if ((fd > 0) && (!follow_symlinks)) {
        PyErr_Format(PyExc_ValueError,
                     "%s: cannot use fd and follow_symlinks together",
                     function_name);
        return 1;
    }
    return 0;
}

static int
dir_fd_and_follow_symlinks_invalid(const char *function_name, int dir_fd,
                                   int follow_symlinks)
{
    if ((dir_fd != DEFAULT_DIR_FD) && (!follow_symlinks)) {
        PyErr_Format(PyExc_ValueError,
                     "%s: cannot use dir_fd and follow_symlinks together",
                     function_name);
        return 1;
    }
    return 0;
}

#ifdef MS_WINDOWS
    typedef long long Py_off_t;
#else
    typedef off_t Py_off_t;
#endif

static int
Py_off_t_converter(PyObject *arg, void *addr)
{
#ifdef HAVE_LARGEFILE_SUPPORT
    *((Py_off_t *)addr) = PyLong_AsLongLong(arg);
#else
    *((Py_off_t *)addr) = PyLong_AsLong(arg);
#endif
    if (PyErr_Occurred())
        return 0;
    return 1;
}

static PyObject *
PyLong_FromPy_off_t(Py_off_t offset)
{
#ifdef HAVE_LARGEFILE_SUPPORT
    return PyLong_FromLongLong(offset);
#else
    return PyLong_FromLong(offset);
#endif
}



/* Set a POSIX-specific error from errno, and return NULL */

static PyObject *
posix_error(void)
{
    return PyErr_SetFromErrno(PyExc_OSError);
}

static PyObject *
posix_path_object_error(PyObject *path)
{
    return PyErr_SetFromErrnoWithFilenameObject(PyExc_OSError, path);
}

static PyObject *
path_object_error(PyObject *path)
{
#ifdef MS_WINDOWS
    return PyErr_SetExcFromWindowsErrWithFilenameObject(
                PyExc_OSError, 0, path);
#else
    return posix_path_object_error(path);
#endif
}

static PyObject *
path_object_error2(PyObject *path, PyObject *path2)
{
#ifdef MS_WINDOWS
    return PyErr_SetExcFromWindowsErrWithFilenameObjects(
                PyExc_OSError, 0, path, path2);
#else
    return PyErr_SetFromErrnoWithFilenameObjects(PyExc_OSError, path, path2);
#endif
}

static PyObject *
path_error(path_t *path)
{
    return path_object_error(path->object);
}

static PyObject *
posix_path_error(path_t *path)
{
    return posix_path_object_error(path->object);
}

static PyObject *
path_error2(path_t *path, path_t *path2)
{
    return path_object_error2(path->object, path2->object);
}


/* POSIX generic methods */

static int
fildes_converter(PyObject *o, void *p)
{
    int fd;
    int *pointer = (int *)p;
    fd = PyObject_AsFileDescriptor(o);
    if (fd < 0)
        return 0;
    *pointer = fd;
    return 1;
}

static PyObject *
posix_fildes_fd(int fd, int (*func)(int))
{
    int res;
    int async_err = 0;

    do {
        Py_BEGIN_ALLOW_THREADS
        _Py_BEGIN_SUPPRESS_IPH
        res = (*func)(fd);
        _Py_END_SUPPRESS_IPH
        Py_END_ALLOW_THREADS
    } while (res != 0 && errno == EINTR && !(async_err = PyErr_CheckSignals()));
    if (res != 0)
        return (!async_err) ? posix_error() : NULL;
    Py_RETURN_NONE;
}



PyDoc_STRVAR(stat_result__doc__,
"stat_result: Result from stat, fstat, or lstat.\n\n\
This object may be accessed either as a tuple of\n\
  (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime)\n\
or via the attributes st_mode, st_ino, st_dev, st_nlink, st_uid, and so on.\n\
\n\
Posix/windows: If your platform supports st_blksize, st_blocks, st_rdev,\n\
or st_flags, they are available as attributes only.\n\
\n\
See os.stat for more information.");

static PyStructSequence_Field stat_result_fields[] = {
    {"st_mode",    "protection bits"},
    {"st_ino",     "inode"},
    {"st_dev",     "device"},
    {"st_nlink",   "number of hard links"},
    {"st_uid",     "user ID of owner"},
    {"st_gid",     "group ID of owner"},
    {"st_size",    "total size, in bytes"},
    {"st_atime",   "time of last access"},
    {"st_mtime",   "time of last modification"},
    {"st_ctime",   "time of last change"},
    {"int_st_atime",   "integer time of last access"},
    {"int_st_mtime",   "integer time of last modification"},
    {"int_st_ctime",   "integer time of last change"},
    {"st_atime_ns",   "time of last access in nanoseconds"},
    {"st_mtime_ns",   "time of last modification in nanoseconds"},
    {"st_ctime_ns",   "time of last change in nanoseconds"},
#ifdef HAVE_STRUCT_STAT_ST_BLKSIZE
    {"st_blksize", "blocksize for filesystem I/O"},
#endif
#ifdef HAVE_STRUCT_STAT_ST_BLOCKS
    {"st_blocks",  "number of blocks allocated"},
#endif
#ifdef HAVE_STRUCT_STAT_ST_RDEV
    {"st_rdev",    "device type (if inode device)"},
#endif
#ifdef HAVE_STRUCT_STAT_ST_FLAGS
    {"st_flags",   "user defined flags for file"},
#endif
#ifdef HAVE_STRUCT_STAT_ST_GEN
    {"st_gen",    "generation number"},
#endif
#ifdef HAVE_STRUCT_STAT_ST_BIRTHTIME
    {"st_birthtime",   "time of creation"},
#endif
#ifdef HAVE_STRUCT_STAT_ST_FILE_ATTRIBUTES
    {"st_file_attributes", "Windows file attribute bits"},
#endif
#ifdef HAVE_STRUCT_STAT_ST_FSTYPE
    {"st_fstype",  "Type of filesystem"},
#endif
#ifdef HAVE_STRUCT_STAT_ST_TAG
    {"st_ft_ccsid",    "file tag ccsid"},
    {"st_ft_txtflag",  "file tag txtflag"},
#endif
#ifdef HAVE_STRUCT_STAT_ST_REPARSE_TAG
    {"st_reparse_tag", "Windows reparse tag"},
#endif
    {0}
};

#define ST_LAST_FIXED_INDEX 15

#ifdef HAVE_STRUCT_STAT_ST_BLKSIZE
#define ST_BLKSIZE_IDX (ST_LAST_FIXED_INDEX+1)
#else
#define ST_BLKSIZE_IDX ST_LAST_FIXED_INDEX
#endif

#ifdef HAVE_STRUCT_STAT_ST_BLOCKS
#define ST_BLOCKS_IDX (ST_BLKSIZE_IDX+1)
#else
#define ST_BLOCKS_IDX ST_BLKSIZE_IDX
#endif

#ifdef HAVE_STRUCT_STAT_ST_RDEV
#define ST_RDEV_IDX (ST_BLOCKS_IDX+1)
#else
#define ST_RDEV_IDX ST_BLOCKS_IDX
#endif

#ifdef HAVE_STRUCT_STAT_ST_FLAGS
#define ST_FLAGS_IDX (ST_RDEV_IDX+1)
#else
#define ST_FLAGS_IDX ST_RDEV_IDX
#endif

#ifdef HAVE_STRUCT_STAT_ST_GEN
#define ST_GEN_IDX (ST_FLAGS_IDX+1)
#else
#define ST_GEN_IDX ST_FLAGS_IDX
#endif

#ifdef HAVE_STRUCT_STAT_ST_BIRTHTIME
#define ST_BIRTHTIME_IDX (ST_GEN_IDX+1)
#else
#define ST_BIRTHTIME_IDX ST_GEN_IDX
#endif

#ifdef HAVE_STRUCT_STAT_ST_FILE_ATTRIBUTES
#define ST_FILE_ATTRIBUTES_IDX (ST_BIRTHTIME_IDX+1)
#else
#define ST_FILE_ATTRIBUTES_IDX ST_BIRTHTIME_IDX
#endif

#ifdef HAVE_STRUCT_STAT_ST_FSTYPE
#define ST_FSTYPE_IDX (ST_FILE_ATTRIBUTES_IDX+1)
#else
#define ST_FSTYPE_IDX ST_FILE_ATTRIBUTES_IDX
#endif

#ifdef HAVE_STRUCT_STAT_ST_REPARSE_TAG
#define ST_REPARSE_TAG_IDX (ST_FSTYPE_IDX+1)
#else
#define ST_REPARSE_TAG_IDX ST_FSTYPE_IDX
#endif

#ifdef HAVE_STRUCT_STAT_ST_TAG
#define ST_CCSID_IDX (ST_REPARSE_TAG_IDX+1)
#define ST_TXTFLAG_IDX (ST_CCSID_IDX+1)
#else
#define ST_CCSID_IDX ST_REPARSE_TAG_IDX
#define ST_TXTFLAG_IDX ST_CCSID_IDX
#endif

#define ST_LAST_INDEX ST_TXTFLAG_IDX

#define STAT_RESULT_SIZE (ST_LAST_INDEX+1)

static PyStructSequence_Desc stat_result_desc = {
    "stat_result", /* name */
    stat_result__doc__, /* doc */
    stat_result_fields,
    STAT_RESULT_SIZE
};

static int initialized;
static PyTypeObject* StatResultType;
static PyTypeObject* StatVFSResultType;
#if defined(HAVE_SCHED_SETPARAM) || defined(HAVE_SCHED_SETSCHEDULER) || defined(POSIX_SPAWN_SETSCHEDULER) || defined(POSIX_SPAWN_SETSCHEDPARAM)
static PyTypeObject* SchedParamType;
#endif
static newfunc structseq_new;

static PyObject *
statresult_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyStructSequence *result;
    int i;

    result = (PyStructSequence*)structseq_new(type, args, kwds);
    if (!result)
        return NULL;
    /* If we have been initialized from a tuple,
       st_?time might be set to None. Initialize it
       from the int slots.  */
    for (i = 7; i < 10; i++) {
        if (result->ob_item[i+3] == Py_None) {
            Py_DECREF(Py_None);
            Py_INCREF(result->ob_item[i]);
            result->ob_item[i+3] = result->ob_item[i];
        }
    }
    return (PyObject*)result;
}


static PyObject *billion = NULL;

static void
fill_time(PyObject *v, int index, time_t sec, unsigned long nsec)
{
    PyObject *s = _PyLong_FromTime_t(sec);
    PyObject *ns_fractional = PyLong_FromUnsignedLong(nsec);
    PyObject *s_in_ns = NULL;
    PyObject *ns_total = NULL;
    PyObject *float_s = NULL;

    if (!(s && ns_fractional))
        goto exit;

    s_in_ns = PyNumber_Multiply(s, billion);
    if (!s_in_ns)
        goto exit;

    ns_total = PyNumber_Add(s_in_ns, ns_fractional);
    if (!ns_total)
        goto exit;

    float_s = PyFloat_FromDouble(sec + 1e-9*nsec);
    if (!float_s) {
        goto exit;
    }

    PyStructSequence_SET_ITEM(v, index, s);
    PyStructSequence_SET_ITEM(v, index+3, float_s);
    PyStructSequence_SET_ITEM(v, index+6, ns_total);
    s = NULL;
    float_s = NULL;
    ns_total = NULL;
exit:
    Py_XDECREF(s);
    Py_XDECREF(ns_fractional);
    Py_XDECREF(s_in_ns);
    Py_XDECREF(ns_total);
    Py_XDECREF(float_s);
}

/* pack a system stat C structure into the Python stat tuple
   (used by posix_stat() and posix_fstat()) */
static PyObject*
_pystat_fromstructstat(STRUCT_STAT *st)
{
    unsigned long ansec, mnsec, cnsec;
    PyObject *v = PyStructSequence_New(StatResultType);
    if (v == NULL)
        return NULL;

    PyStructSequence_SET_ITEM(v, 0, PyLong_FromLong((long)st->st_mode));
    Py_BUILD_ASSERT(sizeof(unsigned long long) >= sizeof(st->st_ino));
    PyStructSequence_SET_ITEM(v, 1, PyLong_FromUnsignedLongLong(st->st_ino));
#ifdef MS_WINDOWS
    PyStructSequence_SET_ITEM(v, 2, PyLong_FromUnsignedLong(st->st_dev));
#else
    PyStructSequence_SET_ITEM(v, 2, _PyLong_FromDev(st->st_dev));
#endif
    PyStructSequence_SET_ITEM(v, 3, PyLong_FromLong((long)st->st_nlink));
#if defined(MS_WINDOWS)
    PyStructSequence_SET_ITEM(v, 4, PyLong_FromLong(0));
    PyStructSequence_SET_ITEM(v, 5, PyLong_FromLong(0));
#else
    PyStructSequence_SET_ITEM(v, 4, _PyLong_FromUid(st->st_uid));
    PyStructSequence_SET_ITEM(v, 5, _PyLong_FromGid(st->st_gid));
#endif
    Py_BUILD_ASSERT(sizeof(long long) >= sizeof(st->st_size));
    PyStructSequence_SET_ITEM(v, 6, PyLong_FromLongLong(st->st_size));

#if defined(HAVE_STAT_TV_NSEC)
    ansec = st->st_atim.tv_nsec;
    mnsec = st->st_mtim.tv_nsec;
    cnsec = st->st_ctim.tv_nsec;
#elif defined(HAVE_STAT_TV_NSEC2)
    ansec = st->st_atimespec.tv_nsec;
    mnsec = st->st_mtimespec.tv_nsec;
    cnsec = st->st_ctimespec.tv_nsec;
#elif defined(HAVE_STAT_NSEC)
    ansec = st->st_atime_nsec;
    mnsec = st->st_mtime_nsec;
    cnsec = st->st_ctime_nsec;
#else
    ansec = mnsec = cnsec = 0;
#endif
    fill_time(v, 7, st->st_atime, ansec);
    fill_time(v, 8, st->st_mtime, mnsec);
    fill_time(v, 9, st->st_ctime, cnsec);

#ifdef HAVE_STRUCT_STAT_ST_BLKSIZE
    PyStructSequence_SET_ITEM(v, ST_BLKSIZE_IDX,
                              PyLong_FromLong((long)st->st_blksize));
#endif
#ifdef HAVE_STRUCT_STAT_ST_BLOCKS
    PyStructSequence_SET_ITEM(v, ST_BLOCKS_IDX,
                              PyLong_FromLong((long)st->st_blocks));
#endif
#ifdef HAVE_STRUCT_STAT_ST_RDEV
    PyStructSequence_SET_ITEM(v, ST_RDEV_IDX,
                              PyLong_FromLong((long)st->st_rdev));
#endif
#ifdef HAVE_STRUCT_STAT_ST_GEN
    PyStructSequence_SET_ITEM(v, ST_GEN_IDX,
                              PyLong_FromLong((long)st->st_gen));
#endif
#ifdef HAVE_STRUCT_STAT_ST_BIRTHTIME
    {
      PyObject *val;
      unsigned long bsec,bnsec;
      bsec = (long)st->st_birthtime;
#ifdef HAVE_STAT_TV_NSEC2
      bnsec = st->st_birthtimespec.tv_nsec;
#else
      bnsec = 0;
#endif
      val = PyFloat_FromDouble(bsec + 1e-9*bnsec);
      PyStructSequence_SET_ITEM(v, ST_BIRTHTIME_IDX,
                                val);
    }
#endif
#ifdef HAVE_STRUCT_STAT_ST_FLAGS
    PyStructSequence_SET_ITEM(v, ST_FLAGS_IDX,
                              PyLong_FromLong((long)st->st_flags));
#endif
#ifdef HAVE_STRUCT_STAT_ST_FILE_ATTRIBUTES
    PyStructSequence_SET_ITEM(v, ST_FILE_ATTRIBUTES_IDX,
                              PyLong_FromUnsignedLong(st->st_file_attributes));
#endif
#ifdef HAVE_STRUCT_STAT_ST_FSTYPE
   PyStructSequence_SET_ITEM(v, ST_FSTYPE_IDX,
                              PyUnicode_FromString(st->st_fstype));
#endif
#ifdef HAVE_STRUCT_STAT_ST_REPARSE_TAG
    PyStructSequence_SET_ITEM(v, ST_REPARSE_TAG_IDX,
                              PyLong_FromUnsignedLong(st->st_reparse_tag));
#endif
#ifdef HAVE_STRUCT_STAT_ST_TAG
    PyStructSequence_SET_ITEM(v, ST_CCSID_IDX, PyLong_FromLong((long)st->st_tag.ft_ccsid));
    PyStructSequence_SET_ITEM(v, ST_TXTFLAG_IDX, PyLong_FromLong((long)st->st_tag.ft_txtflag));
#endif

    if (PyErr_Occurred()) {
        Py_DECREF(v);
        return NULL;
    }

    return v;
}

/* POSIX methods */


static PyObject *
posix_do_stat(const char *function_name, path_t *path,
              int dir_fd, int follow_symlinks)
{
    STRUCT_STAT st;
    int result;

#if !defined(MS_WINDOWS) && !defined(HAVE_FSTATAT) && !defined(HAVE_LSTAT)
    if (follow_symlinks_specified(function_name, follow_symlinks))
        return NULL;
#endif

    if (path_and_dir_fd_invalid("stat", path, dir_fd) ||
        dir_fd_and_fd_invalid("stat", dir_fd, path->fd) ||
        fd_and_follow_symlinks_invalid("stat", path->fd, follow_symlinks))
        return NULL;

    Py_BEGIN_ALLOW_THREADS
    if (path->fd != -1)
        result = FSTAT(path->fd, &st);
#ifdef MS_WINDOWS
    else if (follow_symlinks)
        result = win32_stat(path->wide, &st);
    else
        result = win32_lstat(path->wide, &st);
#else
    else
#if defined(HAVE_LSTAT)
    if ((!follow_symlinks) && (dir_fd == DEFAULT_DIR_FD))
        result = LSTAT(path->narrow, &st);
    else
#endif /* HAVE_LSTAT */
#ifdef HAVE_FSTATAT
    if ((dir_fd != DEFAULT_DIR_FD) || !follow_symlinks)
        result = fstatat(dir_fd, path->narrow, &st,
                         follow_symlinks ? 0 : AT_SYMLINK_NOFOLLOW);
    else
#endif /* HAVE_FSTATAT */
        result = STAT(path->narrow, &st);
#endif /* MS_WINDOWS */
    Py_END_ALLOW_THREADS

    if (result != 0) {
        return path_error(path);
    }

    return _pystat_fromstructstat(&st);
}

#ifdef __MVS__
static int set_chattr_int_field(PyObject *pystat, char *attr_name, int *attr_value)
{
    char parsei[256];
    PyObject *val = PyObject_GetAttrString(pystat, attr_name);
    if (val==NULL) {PyErr_Clear(); val = PyMapping_Check(pystat) ? PyMapping_GetItemString(pystat, attr_name) : NULL;}
    if (val==NULL) {PyErr_Clear(); return 0;}
    snprintf(parsei, sizeof(parsei), "i:chattr() arg 2 contains non integer value for '%s'", attr_name);
    if (!PyArg_Parse(val, parsei, attr_value)) {Py_DECREF(val); return 0;}
    return 1;
}

static int set_chattr_time_field(PyObject *pystat, char *attr_name, time_t *sec_value, long *usec_value)
{
    char parsei[256];
    PyObject *val = PyObject_GetAttrString(pystat, attr_name);
    if (val==NULL) {PyErr_Clear(); val = PyMapping_Check(pystat) ? PyMapping_GetItemString(pystat, attr_name) : NULL;}
    if (val==NULL) {PyErr_Clear(); return 0;}
    if (val==Py_None) {
        *sec_value = 0;
	*usec_value = 0;
    } else if (_PyTime_ObjectToTimespec(val, sec_value, usec_value, _PyTime_ROUND_FLOOR) == -1) {
        Py_DECREF(val);
        PyErr_Format(PyExc_RuntimeError, "chattr() arg 2 contains invalid time value for '%s'", attr_name);
        return 0;
    }
    Py_DECREF(val);
    return 1;
}

PyDoc_STRVAR(posix_chattr__doc__,
"chattr(path, stat result, list of stat attribute names))\n\n\
Change the attributes of a file.");

static PyObject *
posix_chattr(PyObject *self, PyObject *args)
{
    attrib_t attr;
    memset(&attr, 0, sizeof(attr));
    path_t path;
    int res;
    PyObject *pystat;

    memset(&path, 0, sizeof(path));
    if (!PyArg_ParseTuple(args, "O&O:chattr",
                          path_converter, &path, &pystat))
        return NULL;

    PyMappingMethods *m;
    if (!(pystat!=NULL && (m=pystat->ob_type->tp_as_mapping)!=NULL && m->mp_subscript!=NULL)){
        PyErr_SetString(PyExc_TypeError, "chattr() arg 2 must be a mapping");
        goto fail;
    }

    attr.att_modechg=set_chattr_int_field(pystat, "st_mode", &attr.att_mode); if (PyErr_Occurred()) goto fail;
    int have_uid, have_gid;
    if (0) { /* only do these if they will succeed */
      attr.att_ownerchg=have_uid=set_chattr_int_field(pystat, "st_uid", &attr.att_uid); if (PyErr_Occurred()) goto fail;
      attr.att_ownerchg=have_gid=set_chattr_int_field(pystat, "st_gid", &attr.att_gid); if (PyErr_Occurred()) goto fail;
    }
    if (!attr.att_modechg || (attr.att_mode & S_IFMT)==0 || 
	S_ISREG(attr.att_mode) || S_ISFIFO(attr.att_mode) || S_ISCHR(attr.att_mode)) {
      int ccsid, txtflag, have_ccsid, have_txtflag;
      attr.att_filetagchg=have_ccsid=set_chattr_int_field(pystat, "st_ft_ccsid", &ccsid); if (PyErr_Occurred()) goto fail;
      attr.att_filetag.ft_ccsid = (unsigned short)ccsid;
      attr.att_filetagchg=have_txtflag=set_chattr_int_field(pystat, "st_ft_txtflag", &txtflag); if (PyErr_Occurred()) goto fail;
      attr.att_filetag.ft_txtflag = txtflag;
    }
    time_t usec_value;
#define SET_CHATTR_TIME(prefix) \
    attr.att_##prefix##timechg=set_chattr_time_field(pystat, "st_" #prefix "time", &attr.att_##prefix##time, &usec_value); \
    attr.att_##prefix##timetod=(attr.att_##prefix##time==0); \
    if (PyErr_Occurred()) goto fail;
    SET_CHATTR_TIME(a);
    SET_CHATTR_TIME(m);
    SET_CHATTR_TIME(c);
    SET_CHATTR_TIME(ref);
    /* "st_size" att_trunc att_size off_t */
    /* att_filefmtchg:1 att_filefmt char File Format */
    /* att_seclabelchg:1 att_seclabel char Security Label */
    /* att_maaudit:1 att_auditoraudit int */
    /* att_muaudit:1 att_useraudit int  */
    /* att_setgen:1 int 1=Set General Attributes */
    /* att_sharelibmask:1 int 1=Shared Library Mask */
    /* att_noshareasmask:1 int 1=No Shareas Flag Mask */
    /* att_apfauthmask:1 int 1=APF Authorized Flag Mask */
    /* att_progctlmask:1 int 1=Prog. Controlled Flag Mask */
    /* att_sharelib:1 int 1=Shared Library Flag */
    /* att_noshareas:1 int 1=No Shareas Flag */
    /* att_apfauth:1 int 1=APF Authorized Flag */
    /* att_progctl:1 int 1=Program Controlled Flag */
    
    Py_BEGIN_ALLOW_THREADS
    res = __chattr(path.narrow, &attr, sizeof(attr));
    Py_END_ALLOW_THREADS

    if (res != 0)
        return path_error(&path);
    path_cleanup(&path);
    Py_INCREF(Py_None);
    return Py_None;
    fail:
    path_cleanup(&path);
    return NULL;
}
#endif

#ifdef HAVE_FSTATAT
    #define FSTATAT_DIR_FD_CONVERTER dir_fd_converter
#else
    #define FSTATAT_DIR_FD_CONVERTER dir_fd_unavailable
#endif

PyDoc_STRVAR(os_stat__doc__,
"stat($module, /, path, *, dir_fd=None, follow_symlinks=True)\n"
"--\n"
"\n"
"Perform a stat system call on the given path.\n"
"\n"
"  path\n"
"    Path to be examined; can be string, bytes, a path-like object or\n"
"    open-file-descriptor int.\n"
"  dir_fd\n"
"    If not None, it should be a file descriptor open to a directory,\n"
"    and path should be a relative string; path will then be relative to\n"
"    that directory.\n"
"  follow_symlinks\n"
"    If False, and the last element of the path is a symbolic link,\n"
"    stat will examine the symbolic link itself instead of the file\n"
"    the link points to.\n"
"\n"
"dir_fd and follow_symlinks may not be implemented\n"
"  on your platform.  If they are unavailable, using them will raise a\n"
"  NotImplementedError.\n"
"\n"
"It\'s an error to use dir_fd or follow_symlinks when specifying path as\n"
"  an open file descriptor.");

#define OS_STAT_METHODDEF    \
    {"stat", (PyCFunction)(void(*)(void))os_stat, METH_FASTCALL|METH_KEYWORDS, os_stat__doc__},

static PyObject *
os_stat_impl(PyObject *module, path_t *path, int dir_fd, int follow_symlinks);

static PyObject *
os_stat(PyObject *module, PyObject *const *args, Py_ssize_t nargs, PyObject *kwnames)
{
    PyObject *return_value = NULL;
    static const char * const _keywords[] = {"path", "dir_fd", "follow_symlinks", NULL};
    static _PyArg_Parser _parser = {NULL, _keywords, "stat", 0};
    PyObject *argsbuf[3];
    Py_ssize_t noptargs = nargs + (kwnames ? PyTuple_GET_SIZE(kwnames) : 0) - 1;
    path_t path = PATH_T_INITIALIZE("stat", "path", 0, 1);
    int dir_fd = DEFAULT_DIR_FD;
    int follow_symlinks = 1;

    args = _PyArg_UnpackKeywords(args, nargs, NULL, kwnames, &_parser, 1, 1, 0, argsbuf);
    if (!args) {
        goto exit;
    }
    if (!path_converter(args[0], &path)) {
        goto exit;
    }
    if (!noptargs) {
        goto skip_optional_kwonly;
    }
    if (args[1]) {
        if (!FSTATAT_DIR_FD_CONVERTER(args[1], &dir_fd)) {
            goto exit;
        }
        if (!--noptargs) {
            goto skip_optional_kwonly;
        }
    }
    follow_symlinks = PyObject_IsTrue(args[2]);
    if (follow_symlinks < 0) {
        goto exit;
    }
skip_optional_kwonly:
    return_value = os_stat_impl(module, &path, dir_fd, follow_symlinks);

exit:
    /* Cleanup for path */
    path_cleanup(&path);

    return return_value;
}

PyDoc_STRVAR(os_lstat__doc__,
"lstat($module, /, path, *, dir_fd=None)\n"
"--\n"
"\n"
"Perform a stat system call on the given path, without following symbolic links.\n"
"\n"
"Like stat(), but do not follow symbolic links.\n"
"Equivalent to stat(path, follow_symlinks=False).");

#define OS_LSTAT_METHODDEF    \
    {"lstat", (PyCFunction)(void(*)(void))os_lstat, METH_FASTCALL|METH_KEYWORDS, os_lstat__doc__},

static PyObject *
os_lstat_impl(PyObject *module, path_t *path, int dir_fd);

static PyObject *
os_lstat(PyObject *module, PyObject *const *args, Py_ssize_t nargs, PyObject *kwnames)
{
    PyObject *return_value = NULL;
    static const char * const _keywords[] = {"path", "dir_fd", NULL};
    static _PyArg_Parser _parser = {NULL, _keywords, "lstat", 0};
    PyObject *argsbuf[2];
    Py_ssize_t noptargs = nargs + (kwnames ? PyTuple_GET_SIZE(kwnames) : 0) - 1;
    path_t path = PATH_T_INITIALIZE("lstat", "path", 0, 0);
    int dir_fd = DEFAULT_DIR_FD;

    args = _PyArg_UnpackKeywords(args, nargs, NULL, kwnames, &_parser, 1, 1, 0, argsbuf);
    if (!args) {
        goto exit;
    }
    if (!path_converter(args[0], &path)) {
        goto exit;
    }
    if (!noptargs) {
        goto skip_optional_kwonly;
    }
    if (!FSTATAT_DIR_FD_CONVERTER(args[1], &dir_fd)) {
        goto exit;
    }
skip_optional_kwonly:
    return_value = os_lstat_impl(module, &path, dir_fd);

exit:
    /* Cleanup for path */
    path_cleanup(&path);

    return return_value;
}

static PyObject *
os_stat_impl(PyObject *module, path_t *path, int dir_fd, int follow_symlinks)
/*[clinic end generated code: output=7d4976e6f18a59c5 input=01d362ebcc06996b]*/
{
    return posix_do_stat("stat", path, dir_fd, follow_symlinks);
}


static PyObject *
os_lstat_impl(PyObject *module, path_t *path, int dir_fd)
/*[clinic end generated code: output=ef82a5d35ce8ab37 input=0b7474765927b925]*/
{
    int follow_symlinks = 0;
    return posix_do_stat("lstat", path, dir_fd, follow_symlinks);
}


PyDoc_STRVAR(os_uname__doc__,
"uname($module, /, *, compatible=False)\n"
"--\n"
"\n"
"Return an object identifying the current operating system.\n"
"\n"
"The object behaves like a named tuple with the following fields:\n"
"  (sysname, nodename, release, version, machine)\n"
"\n"
"compatible is a boolean, True means use \"uname\", False means \"uname -I\"\n"
"  The compatible=True values are guaranteed monotonic, but are unfamiliar to most users\n"
"  The compatible=False values give the current Operating System names and versions");

#define OS_UNAME_METHODDEF    \
    {"uname", (PyCFunction)os_uname, METH_FASTCALL|METH_KEYWORDS, os_uname__doc__},

static PyObject *
os_uname_impl(PyObject *module, int compatible);

static PyObject *
os_uname(PyObject *module, PyObject **args, Py_ssize_t nargs, PyObject *kwnames)
{
    PyObject *return_value = NULL;
    static const char * const _keywords[] = {"compatible", NULL};
    static _PyArg_Parser _parser = {"|p:uname", _keywords, 0};
    int compatible = 0;

    if (!_PyArg_ParseStackAndKeywords(args, nargs, kwnames, &_parser,
				      &compatible)) {
        goto exit;
    }
    
    return_value = os_uname_impl(module, compatible);

 exit:
    return return_value;
}

static PyStructSequence_Field uname_result_fields[] = {
    {"sysname",    "operating system name"},
    {"nodename",   "name of machine on network (implementation-defined)"},
    {"release",    "operating system release"},
    {"version",    "operating system version"},
    {"machine",    "hardware identifier"},
    {NULL}
};

PyDoc_STRVAR(uname_result__doc__,
"uname_result: Result from os.uname().\n\n\
This object may be accessed either as a tuple of\n\
  (sysname, nodename, release, version, machine),\n\
or via the attributes sysname, nodename, release, version, and machine.\n\
\n\
See os.uname for more information.");

static PyStructSequence_Desc uname_result_desc = {
    "uname_result", /* name */
    uname_result__doc__, /* doc */
    uname_result_fields,
    5
};

static PyTypeObject* UnameResultType;


#ifdef HAVE_UNAME
/*[clinic input]
os.uname

Return an object identifying the current operating system.

The object behaves like a named tuple with the following fields:
  (sysname, nodename, release, version, machine)

[clinic start generated code]*/

static PyObject *
os_uname_impl(PyObject *module, int compatible)
/*[clinic end generated code: output=e6a49cf1a1508a19 input=e68bd246db3043ed]*/
{
    struct utsname u;
    int res;
    PyObject *value;

    Py_BEGIN_ALLOW_THREADS
    if (compatible)  
	res = uname(&u);
    else
        res = __osname(&u);
    Py_END_ALLOW_THREADS
    if (res < 0)
        return posix_error();

    value = PyStructSequence_New(UnameResultType);
    if (value == NULL)
        return NULL;

#define SET(i, field) \
    { \
    PyObject *o = PyUnicode_DecodeFSDefault(field); \
    if (!o) { \
        Py_DECREF(value); \
        return NULL; \
    } \
    PyStructSequence_SET_ITEM(value, i, o); \
    } \

    SET(0, u.sysname);
    SET(1, u.nodename);
    SET(2, u.release);
    SET(3, u.version);
    SET(4, u.machine);

#undef SET

    return value;
}


PyDoc_STRVAR(os_readlink__doc__,
"readlink($module, /, path, *, dir_fd=None)\n"
"--\n"
"\n"
"Return a string representing the path to which the symbolic link points.\n"
"\n"
"If dir_fd is not None, it should be a file descriptor open to a directory,\n"
"and path should be relative; path will then be relative to that directory.\n"
"\n"
"dir_fd may not be implemented on your platform.  If it is unavailable,\n"
"using it will raise a NotImplementedError.");

#define OS_READLINK_METHODDEF    \
    {"readlink", (PyCFunction)(void(*)(void))os_readlink, METH_FASTCALL|METH_KEYWORDS, os_readlink__doc__},

static PyObject *
os_readlink_impl(PyObject *module, path_t *path, int dir_fd);

static PyObject *
os_readlink(PyObject *module, PyObject *const *args, Py_ssize_t nargs, PyObject *kwnames)
{
    PyObject *return_value = NULL;
    static const char * const _keywords[] = {"path", "dir_fd", NULL};
    static _PyArg_Parser _parser = {NULL, _keywords, "readlink", 0};
    PyObject *argsbuf[2];
    Py_ssize_t noptargs = nargs + (kwnames ? PyTuple_GET_SIZE(kwnames) : 0) - 1;
    path_t path = PATH_T_INITIALIZE("readlink", "path", 0, 0);
    int dir_fd = DEFAULT_DIR_FD;

    args = _PyArg_UnpackKeywords(args, nargs, NULL, kwnames, &_parser, 1, 1, 0, argsbuf);
    if (!args) {
        goto exit;
    }
    if (!path_converter(args[0], &path)) {
        goto exit;
    }
    if (!noptargs) {
        goto skip_optional_kwonly;
    }
    if (!READLINKAT_DIR_FD_CONVERTER(args[1], &dir_fd)) {
        goto exit;
    }
skip_optional_kwonly:
    return_value = os_readlink_impl(module, &path, dir_fd);

exit:
    /* Cleanup for path */
    path_cleanup(&path);

    return return_value;
}

static PyObject *
os_readlink_impl(PyObject *module, path_t *path, int dir_fd)
/*[clinic end generated code: output=d21b732a2e814030 input=113c87e0db1ecaf2]*/
{
#if defined(HAVE_READLINK)
    char buffer[MAXPATHLEN+1];
    char *realpath_result = NULL;
    ssize_t length;

    Py_BEGIN_ALLOW_THREADS
#ifdef HAVE_READLINKAT
    if (dir_fd != DEFAULT_DIR_FD)
        length = readlinkat(dir_fd, path->narrow, buffer, MAXPATHLEN);
    else
#endif
        length = readlink(path->narrow, buffer, MAXPATHLEN);
#ifdef __MVS__
    buffer[MAXPATHLEN]=0;
    if (length > 0 &&
	(0 == strncmp(buffer, "$VERSION", strlen("$VERSION")) || 0 == strncmp(buffer, "$SYS", strlen("$SYS")))) {
        if (NULL ==  realpath(path->narrow, buffer))
	    length = -1;
	else
	    length = strlen(buffer);
    }
#endif
    Py_END_ALLOW_THREADS

    if (length < 0) {
        return path_error(path);
    }
    buffer[length] = '\0';

    if (PyUnicode_Check(path->object))
        return PyUnicode_DecodeFSDefaultAndSize(buffer, length);
    else
        return PyBytes_FromStringAndSize(buffer, length);
#endif
}

/*[clinic input]
class os.DirEntry "DirEntry *" "&DirEntryType"
[clinic start generated code]*/
/*[clinic end generated code: output=da39a3ee5e6b4b0d input=3138f09f7c683f1d]*/

typedef struct {
    PyObject_HEAD
    PyObject *name;
    PyObject *path;
    PyObject *stat;
    PyObject *lstat;
#ifdef MS_WINDOWS
    struct _Py_stat_struct win32_lstat;
    uint64_t win32_file_index;
    int got_file_index;
#else /* POSIX */
#ifdef HAVE_DIRENT_D_TYPE
    unsigned char d_type;
#endif
    ino_t d_ino;
    int dir_fd;
#endif
} DirEntry;

static void
DirEntry_dealloc(DirEntry *entry)
{
    Py_XDECREF(entry->name);
    Py_XDECREF(entry->path);
    Py_XDECREF(entry->stat);
    Py_XDECREF(entry->lstat);
    Py_TYPE(entry)->tp_free((PyObject *)entry);
}

/* Forward reference */
static int
DirEntry_test_mode(DirEntry *self, int follow_symlinks, unsigned int mode_bits);

/*[clinic input]
os.DirEntry.is_symlink -> bool

Return True if the entry is a symbolic link; cached per entry.
[clinic start generated code]*/

static int
os_DirEntry_is_symlink_impl(DirEntry *self)
/*[clinic end generated code: output=42244667d7bcfc25 input=1605a1b4b96976c3]*/
{
#ifdef MS_WINDOWS
    return (self->win32_lstat.st_mode & S_IFMT) == S_IFLNK;
#elif defined(HAVE_DIRENT_D_TYPE)
    /* POSIX */
    if (self->d_type != DT_UNKNOWN)
        return self->d_type == DT_LNK;
    else
        return DirEntry_test_mode(self, 0, S_IFLNK);
#else
    /* POSIX without d_type */
    return DirEntry_test_mode(self, 0, S_IFLNK);
#endif
}

static PyObject *
DirEntry_fetch_stat(DirEntry *self, int follow_symlinks)
{
    int result;
    STRUCT_STAT st;
    PyObject *ub;

#ifdef MS_WINDOWS
    if (!PyUnicode_FSDecoder(self->path, &ub))
        return NULL;
    const wchar_t *path = PyUnicode_AsUnicode(ub);
#else /* POSIX */
    if (!PyUnicode_FSConverter(self->path, &ub))
        return NULL;
    const char *path = PyBytes_AS_STRING(ub);
    if (self->dir_fd != DEFAULT_DIR_FD) {
#ifdef HAVE_FSTATAT
        result = fstatat(self->dir_fd, path, &st,
                         follow_symlinks ? 0 : AT_SYMLINK_NOFOLLOW);
#else
        PyErr_SetString(PyExc_NotImplementedError, "can't fetch stat");
        return NULL;
#endif /* HAVE_FSTATAT */
    }
    else
#endif
    {
        if (follow_symlinks)
            result = STAT(path, &st);
        else
            result = LSTAT(path, &st);
    }
    Py_DECREF(ub);

    if (result != 0)
        return path_object_error(self->path);

    return _pystat_fromstructstat(&st);
}

static PyObject *
DirEntry_get_lstat(DirEntry *self)
{
    if (!self->lstat) {
#ifdef MS_WINDOWS
        self->lstat = _pystat_fromstructstat(&self->win32_lstat);
#else /* POSIX */
        self->lstat = DirEntry_fetch_stat(self, 0);
#endif
    }
    Py_XINCREF(self->lstat);
    return self->lstat;
}

/*[clinic input]
os.DirEntry.stat
    *
    follow_symlinks: bool = True

Return stat_result object for the entry; cached per entry.
[clinic start generated code]*/

static PyObject *
os_DirEntry_stat_impl(DirEntry *self, int follow_symlinks)
/*[clinic end generated code: output=008593b3a6d01305 input=280d14c1d6f1d00d]*/
{
    if (!follow_symlinks)
        return DirEntry_get_lstat(self);

    if (!self->stat) {
        int result = os_DirEntry_is_symlink_impl(self);
        if (result == -1)
            return NULL;
        else if (result)
            self->stat = DirEntry_fetch_stat(self, 1);
        else
            self->stat = DirEntry_get_lstat(self);
    }

    Py_XINCREF(self->stat);
    return self->stat;
}

/* Set exception and return -1 on error, 0 for False, 1 for True */
static int
DirEntry_test_mode(DirEntry *self, int follow_symlinks, unsigned int mode_bits)
{
    PyObject *stat = NULL;
    PyObject *st_mode = NULL;
    long mode;
    int result;
#if defined(MS_WINDOWS) || defined(HAVE_DIRENT_D_TYPE)
    int is_symlink;
    int need_stat;
#endif
#ifdef MS_WINDOWS
    unsigned long dir_bits;
#endif
    _Py_IDENTIFIER(st_mode);

#ifdef MS_WINDOWS
    is_symlink = (self->win32_lstat.st_mode & S_IFMT) == S_IFLNK;
    need_stat = follow_symlinks && is_symlink;
#elif defined(HAVE_DIRENT_D_TYPE)
    is_symlink = self->d_type == DT_LNK;
    need_stat = self->d_type == DT_UNKNOWN || (follow_symlinks && is_symlink);
#endif

#if defined(MS_WINDOWS) || defined(HAVE_DIRENT_D_TYPE)
    if (need_stat) {
#endif
        stat = os_DirEntry_stat_impl(self, follow_symlinks);
        if (!stat) {
            if (PyErr_ExceptionMatches(PyExc_FileNotFoundError)) {
                /* If file doesn't exist (anymore), then return False
                   (i.e., say it's not a file/directory) */
                PyErr_Clear();
                return 0;
            }
            goto error;
        }
        st_mode = _PyObject_GetAttrId(stat, &PyId_st_mode);
        if (!st_mode)
            goto error;

        mode = PyLong_AsLong(st_mode);
        if (mode == -1 && PyErr_Occurred())
            goto error;
        Py_CLEAR(st_mode);
        Py_CLEAR(stat);
        result = (mode & S_IFMT) == mode_bits;
#if defined(MS_WINDOWS) || defined(HAVE_DIRENT_D_TYPE)
    }
    else if (is_symlink) {
        assert(mode_bits != S_IFLNK);
        result = 0;
    }
    else {
        assert(mode_bits == S_IFDIR || mode_bits == S_IFREG);
#ifdef MS_WINDOWS
        dir_bits = self->win32_lstat.st_file_attributes & FILE_ATTRIBUTE_DIRECTORY;
        if (mode_bits == S_IFDIR)
            result = dir_bits != 0;
        else
            result = dir_bits == 0;
#else /* POSIX */
        if (mode_bits == S_IFDIR)
            result = self->d_type == DT_DIR;
        else
            result = self->d_type == DT_REG;
#endif
    }
#endif

    return result;

error:
    Py_XDECREF(st_mode);
    Py_XDECREF(stat);
    return -1;
}

/*[clinic input]
os.DirEntry.is_dir -> bool
    *
    follow_symlinks: bool = True

Return True if the entry is a directory; cached per entry.
[clinic start generated code]*/

static int
os_DirEntry_is_dir_impl(DirEntry *self, int follow_symlinks)
/*[clinic end generated code: output=ad2e8d54365da287 input=0135232766f53f58]*/
{
    return DirEntry_test_mode(self, follow_symlinks, S_IFDIR);
}

/*[clinic input]
os.DirEntry.is_file -> bool
    *
    follow_symlinks: bool = True

Return True if the entry is a file; cached per entry.
[clinic start generated code]*/

static int
os_DirEntry_is_file_impl(DirEntry *self, int follow_symlinks)
/*[clinic end generated code: output=8462ade481d8a476 input=0dc90be168b041ee]*/
{
    return DirEntry_test_mode(self, follow_symlinks, S_IFREG);
}

/*[clinic input]
os.DirEntry.inode

Return inode of the entry; cached per entry.
[clinic start generated code]*/

static PyObject *
os_DirEntry_inode_impl(DirEntry *self)
/*[clinic end generated code: output=156bb3a72162440e input=3ee7b872ae8649f0]*/
{
#ifdef MS_WINDOWS
    if (!self->got_file_index) {
        PyObject *unicode;
        const wchar_t *path;
        STRUCT_STAT stat;
        int result;

        if (!PyUnicode_FSDecoder(self->path, &unicode))
            return NULL;
        path = PyUnicode_AsUnicode(unicode);
        result = LSTAT(path, &stat);
        Py_DECREF(unicode);

        if (result != 0)
            return path_object_error(self->path);

        self->win32_file_index = stat.st_ino;
        self->got_file_index = 1;
    }
    Py_BUILD_ASSERT(sizeof(unsigned long long) >= sizeof(self->win32_file_index));
    return PyLong_FromUnsignedLongLong(self->win32_file_index);
#else /* POSIX */
    Py_BUILD_ASSERT(sizeof(unsigned long long) >= sizeof(self->d_ino));
    return PyLong_FromUnsignedLongLong(self->d_ino);
#endif
}

static PyObject *
DirEntry_repr(DirEntry *self)
{
    return PyUnicode_FromFormat("<DirEntry %R>", self->name);
}

/*[clinic input]
os.DirEntry.__fspath__

Returns the path for the entry.
[clinic start generated code]*/

static PyObject *
os_DirEntry___fspath___impl(DirEntry *self)
/*[clinic end generated code: output=6dd7f7ef752e6f4f input=3c49d0cf38df4fac]*/
{
    Py_INCREF(self->path);
    return self->path;
}

static PyMemberDef DirEntry_members[] = {
    {"name", T_OBJECT_EX, offsetof(DirEntry, name), READONLY,
     "the entry's base filename, relative to scandir() \"path\" argument"},
    {"path", T_OBJECT_EX, offsetof(DirEntry, path), READONLY,
     "the entry's full path name; equivalent to os.path.join(scandir_path, entry.name)"},
    {NULL}
};

#include "clinic/posixmodule.c.h"

static PyMethodDef DirEntry_methods[] = {
    OS_DIRENTRY_IS_DIR_METHODDEF
    OS_DIRENTRY_IS_FILE_METHODDEF
    OS_DIRENTRY_IS_SYMLINK_METHODDEF
    OS_DIRENTRY_STAT_METHODDEF
    OS_DIRENTRY_INODE_METHODDEF
    OS_DIRENTRY___FSPATH___METHODDEF
    {NULL}
};

static PyTypeObject DirEntryType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    MODNAME ".DirEntry",                    /* tp_name */
    sizeof(DirEntry),                       /* tp_basicsize */
    0,                                      /* tp_itemsize */
    /* methods */
    (destructor)DirEntry_dealloc,           /* tp_dealloc */
    0,                                      /* tp_vectorcall_offset */
    0,                                      /* tp_getattr */
    0,                                      /* tp_setattr */
    0,                                      /* tp_as_async */
    (reprfunc)DirEntry_repr,                /* tp_repr */
    0,                                      /* tp_as_number */
    0,                                      /* tp_as_sequence */
    0,                                      /* tp_as_mapping */
    0,                                      /* tp_hash */
    0,                                      /* tp_call */
    0,                                      /* tp_str */
    0,                                      /* tp_getattro */
    0,                                      /* tp_setattro */
    0,                                      /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT,                     /* tp_flags */
    0,                                      /* tp_doc */
    0,                                      /* tp_traverse */
    0,                                      /* tp_clear */
    0,                                      /* tp_richcompare */
    0,                                      /* tp_weaklistoffset */
    0,                                      /* tp_iter */
    0,                                      /* tp_iternext */
    DirEntry_methods,                       /* tp_methods */
    DirEntry_members,                       /* tp_members */
};


static char *
join_path_filename(const char *path_narrow, const char* filename, Py_ssize_t filename_len)
{
    Py_ssize_t path_len;
    Py_ssize_t size;
    char *result;

    if (!path_narrow) { /* Default arg: "." */
        path_narrow = ".";
        path_len = 1;
    }
    else {
        path_len = strlen(path_narrow);
    }

    if (filename_len == -1)
        filename_len = strlen(filename);

    /* The +1's are for the path separator and the NUL */
    size = path_len + 1 + filename_len + 1;
    result = PyMem_New(char, size);
    if (!result) {
        PyErr_NoMemory();
        return NULL;
    }
    strcpy(result, path_narrow);
    if (path_len > 0 && result[path_len - 1] != '/')
        result[path_len++] = '/';
    strcpy(result + path_len, filename);
    return result;
}

static PyObject *
DirEntry_from_posix_info(path_t *path, const char *name, Py_ssize_t name_len,
                         ino_t d_ino
#ifdef HAVE_DIRENT_D_TYPE
                         , unsigned char d_type
#endif
                         )
{
    DirEntry *entry;
    char *joined_path;

    entry = PyObject_New(DirEntry, &DirEntryType);
    if (!entry)
        return NULL;
    entry->name = NULL;
    entry->path = NULL;
    entry->stat = NULL;
    entry->lstat = NULL;

    if (path->fd != -1) {
        entry->dir_fd = path->fd;
        joined_path = NULL;
    }
    else {
        entry->dir_fd = DEFAULT_DIR_FD;
        joined_path = join_path_filename(path->narrow, name, name_len);
        if (!joined_path)
            goto error;
    }

    if (!path->narrow || !PyObject_CheckBuffer(path->object)) {
        entry->name = PyUnicode_DecodeFSDefaultAndSize(name, name_len);
        if (joined_path)
            entry->path = PyUnicode_DecodeFSDefault(joined_path);
    }
    else {
        entry->name = PyBytes_FromStringAndSize(name, name_len);
        if (joined_path)
            entry->path = PyBytes_FromString(joined_path);
    }
    PyMem_Free(joined_path);
    if (!entry->name)
        goto error;

    if (path->fd != -1) {
        entry->path = entry->name;
        Py_INCREF(entry->path);
    }
    else if (!entry->path)
        goto error;

#ifdef HAVE_DIRENT_D_TYPE
    entry->d_type = d_type;
#endif
    entry->d_ino = d_ino;

    return (PyObject *)entry;

error:
    Py_XDECREF(entry);
    return NULL;
}



typedef struct {
    PyObject_HEAD
    path_t path;
#ifdef MS_WINDOWS
    HANDLE handle;
    WIN32_FIND_DATAW file_data;
    int first_time;
#else /* POSIX */
    DIR *dirp;
#endif
#ifdef HAVE_FDOPENDIR
    int fd;
#endif
} ScandirIterator;

#ifdef MS_WINDOWS

static int
ScandirIterator_is_closed(ScandirIterator *iterator)
{
    return iterator->handle == INVALID_HANDLE_VALUE;
}

static void
ScandirIterator_closedir(ScandirIterator *iterator)
{
    HANDLE handle = iterator->handle;

    if (handle == INVALID_HANDLE_VALUE)
        return;

    iterator->handle = INVALID_HANDLE_VALUE;
    Py_BEGIN_ALLOW_THREADS
    FindClose(handle);
    Py_END_ALLOW_THREADS
}

static PyObject *
ScandirIterator_iternext(ScandirIterator *iterator)
{
    WIN32_FIND_DATAW *file_data = &iterator->file_data;
    BOOL success;
    PyObject *entry;

    /* Happens if the iterator is iterated twice, or closed explicitly */
    if (iterator->handle == INVALID_HANDLE_VALUE)
        return NULL;

    while (1) {
        if (!iterator->first_time) {
            Py_BEGIN_ALLOW_THREADS
            success = FindNextFileW(iterator->handle, file_data);
            Py_END_ALLOW_THREADS
            if (!success) {
                /* Error or no more files */
                if (GetLastError() != ERROR_NO_MORE_FILES)
                    path_error(&iterator->path);
                break;
            }
        }
        iterator->first_time = 0;

        /* Skip over . and .. */
        if (wcscmp(file_data->cFileName, L".") != 0 &&
            wcscmp(file_data->cFileName, L"..") != 0) {
            entry = DirEntry_from_find_data(&iterator->path, file_data);
            if (!entry)
                break;
            return entry;
        }

        /* Loop till we get a non-dot directory or finish iterating */
    }

    /* Error or no more files */
    ScandirIterator_closedir(iterator);
    return NULL;
}

#else /* POSIX */

static int
ScandirIterator_is_closed(ScandirIterator *iterator)
{
    return !iterator->dirp;
}

static void
ScandirIterator_closedir(ScandirIterator *iterator)
{
    DIR *dirp = iterator->dirp;

    if (!dirp)
        return;

    iterator->dirp = NULL;
    Py_BEGIN_ALLOW_THREADS
#ifdef HAVE_FDOPENDIR
    if (iterator->path.fd != -1)
        rewinddir(dirp);
#endif
    closedir(dirp);
    Py_END_ALLOW_THREADS
    return;
}

static PyObject *
ScandirIterator_iternext(ScandirIterator *iterator)
{
    struct dirent *direntp;
    Py_ssize_t name_len;
    int is_dot;
    PyObject *entry;

    /* Happens if the iterator is iterated twice, or closed explicitly */
    if (!iterator->dirp)
        return NULL;

    while (1) {
        errno = 0;
        Py_BEGIN_ALLOW_THREADS
        direntp = readdir(iterator->dirp);
        Py_END_ALLOW_THREADS

        if (!direntp) {
            /* Error or no more files */
            if (errno != 0)
                path_error(&iterator->path);
            break;
        }

        /* Skip over . and .. */
        name_len = NAMLEN(direntp);
        is_dot = direntp->d_name[0] == '.' &&
                 (name_len == 1 || (direntp->d_name[1] == '.' && name_len == 2));
        if (!is_dot) {
            entry = DirEntry_from_posix_info(&iterator->path, direntp->d_name,
                                            name_len, direntp->d_ino
#ifdef HAVE_DIRENT_D_TYPE
                                            , direntp->d_type
#endif
                                            );
            if (!entry)
                break;
            return entry;
        }

        /* Loop till we get a non-dot directory or finish iterating */
    }

    /* Error or no more files */
    ScandirIterator_closedir(iterator);
    return NULL;
}

#endif

static PyObject *
ScandirIterator_close(ScandirIterator *self, PyObject *args)
{
    ScandirIterator_closedir(self);
    Py_RETURN_NONE;
}

static PyObject *
ScandirIterator_enter(PyObject *self, PyObject *args)
{
    Py_INCREF(self);
    return self;
}

static PyObject *
ScandirIterator_exit(ScandirIterator *self, PyObject *args)
{
    ScandirIterator_closedir(self);
    Py_RETURN_NONE;
}

static void
ScandirIterator_finalize(ScandirIterator *iterator)
{
    PyObject *error_type, *error_value, *error_traceback;

    /* Save the current exception, if any. */
    PyErr_Fetch(&error_type, &error_value, &error_traceback);

    if (!ScandirIterator_is_closed(iterator)) {
        ScandirIterator_closedir(iterator);

        if (PyErr_ResourceWarning((PyObject *)iterator, 1,
                                  "unclosed scandir iterator %R", iterator)) {
            /* Spurious errors can appear at shutdown */
            if (PyErr_ExceptionMatches(PyExc_Warning)) {
                PyErr_WriteUnraisable((PyObject *) iterator);
            }
        }
    }

    path_cleanup(&iterator->path);

    /* Restore the saved exception. */
    PyErr_Restore(error_type, error_value, error_traceback);
}

static void
ScandirIterator_dealloc(ScandirIterator *iterator)
{
    if (PyObject_CallFinalizerFromDealloc((PyObject *)iterator) < 0)
        return;

    Py_TYPE(iterator)->tp_free((PyObject *)iterator);
}

static PyMethodDef ScandirIterator_methods[] = {
    {"__enter__", (PyCFunction)ScandirIterator_enter, METH_NOARGS},
    {"__exit__", (PyCFunction)ScandirIterator_exit, METH_VARARGS},
    {"close", (PyCFunction)ScandirIterator_close, METH_NOARGS},
    {NULL}
};

static PyTypeObject ScandirIteratorType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    MODNAME ".ScandirIterator",             /* tp_name */
    sizeof(ScandirIterator),                /* tp_basicsize */
    0,                                      /* tp_itemsize */
    /* methods */
    (destructor)ScandirIterator_dealloc,    /* tp_dealloc */
    0,                                      /* tp_vectorcall_offset */
    0,                                      /* tp_getattr */
    0,                                      /* tp_setattr */
    0,                                      /* tp_as_async */
    0,                                      /* tp_repr */
    0,                                      /* tp_as_number */
    0,                                      /* tp_as_sequence */
    0,                                      /* tp_as_mapping */
    0,                                      /* tp_hash */
    0,                                      /* tp_call */
    0,                                      /* tp_str */
    0,                                      /* tp_getattro */
    0,                                      /* tp_setattro */
    0,                                      /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT,                     /* tp_flags */
    0,                                      /* tp_doc */
    0,                                      /* tp_traverse */
    0,                                      /* tp_clear */
    0,                                      /* tp_richcompare */
    0,                                      /* tp_weaklistoffset */
    PyObject_SelfIter,                      /* tp_iter */
    (iternextfunc)ScandirIterator_iternext, /* tp_iternext */
    ScandirIterator_methods,                /* tp_methods */
    0,                                      /* tp_members */
    0,                                      /* tp_getset */
    0,                                      /* tp_base */
    0,                                      /* tp_dict */
    0,                                      /* tp_descr_get */
    0,                                      /* tp_descr_set */
    0,                                      /* tp_dictoffset */
    0,                                      /* tp_init */
    0,                                      /* tp_alloc */
    0,                                      /* tp_new */
    0,                                      /* tp_free */
    0,                                      /* tp_is_gc */
    0,                                      /* tp_bases */
    0,                                      /* tp_mro */
    0,                                      /* tp_cache */
    0,                                      /* tp_subclasses */
    0,                                      /* tp_weaklist */
    0,                                      /* tp_del */
    0,                                      /* tp_version_tag */
    (destructor)ScandirIterator_finalize,   /* tp_finalize */
};

/*[clinic input]
os.scandir

    path : path_t(nullable=True, allow_fd='PATH_HAVE_FDOPENDIR') = None

Return an iterator of DirEntry objects for given path.

path can be specified as either str, bytes, or a path-like object.  If path
is bytes, the names of yielded DirEntry objects will also be bytes; in
all other circumstances they will be str.

If path is None, uses the path='.'.
[clinic start generated code]*/

static PyObject *
os_scandir_impl(PyObject *module, path_t *path)
/*[clinic end generated code: output=6eb2668b675ca89e input=6bdd312708fc3bb0]*/
{
    ScandirIterator *iterator;
#ifdef MS_WINDOWS
    wchar_t *path_strW;
#else
    const char *path_str;
#ifdef HAVE_FDOPENDIR
    int fd = -1;
#endif
#endif

    if (PySys_Audit("os.scandir", "O",
                    path->object ? path->object : Py_None) < 0) {
        return NULL;
    }

    iterator = PyObject_New(ScandirIterator, &ScandirIteratorType);
    if (!iterator)
        return NULL;

#ifdef MS_WINDOWS
    iterator->handle = INVALID_HANDLE_VALUE;
#else
    iterator->dirp = NULL;
#endif

    memcpy(&iterator->path, path, sizeof(path_t));
    /* Move the ownership to iterator->path */
    path->object = NULL;
    path->cleanup = NULL;

#ifdef MS_WINDOWS
    iterator->first_time = 1;

    path_strW = join_path_filenameW(iterator->path.wide, L"*.*");
    if (!path_strW)
        goto error;

    Py_BEGIN_ALLOW_THREADS
    iterator->handle = FindFirstFileW(path_strW, &iterator->file_data);
    Py_END_ALLOW_THREADS

    PyMem_Free(path_strW);

    if (iterator->handle == INVALID_HANDLE_VALUE) {
        path_error(&iterator->path);
        goto error;
    }
#else /* POSIX */
    errno = 0;
#ifdef HAVE_FDOPENDIR
    if (path->fd != -1) {
        /* closedir() closes the FD, so we duplicate it */
        fd = _Py_dup(path->fd);
        if (fd == -1)
            goto error;

        Py_BEGIN_ALLOW_THREADS
        iterator->dirp = fdopendir(fd);
        Py_END_ALLOW_THREADS
    }
    else
#endif
    {
        if (iterator->path.narrow)
            path_str = iterator->path.narrow;
        else
            path_str = ".";

        Py_BEGIN_ALLOW_THREADS
        iterator->dirp = opendir(path_str);
        Py_END_ALLOW_THREADS
    }

    if (!iterator->dirp) {
        path_error(&iterator->path);
#ifdef HAVE_FDOPENDIR
        if (fd != -1) {
            Py_BEGIN_ALLOW_THREADS
            close(fd);
            Py_END_ALLOW_THREADS
        }
#endif
        goto error;
    }
#endif

    return (PyObject *)iterator;

error:
    Py_DECREF(iterator);
    return NULL;
}



#ifdef __MVS__
PyDoc_STRVAR(os_zos_system_call__doc__,
"B.zos_system_call() -> B\n\
\n\
more soon.");

/* r15, r0, r1, code_or_save, type */
#define SYSTEM_CALL__SVC    1
#define SYSTEM_CALL__PC     2
#define SYSTEM_CALL__CALL   3
#define SYSTEM_CALL__CALL31 4
       
static PyObject *
os_zos_system_call(PyObject *self, PyObject *args)
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
#endif	

static PyMethodDef posix_methods[] = {
    OS_STAT_METHODDEF
    OS_LISTDIR_METHODDEF
    OS_LSTAT_METHODDEF
    OS_READLINK_METHODDEF
    OS_UNAME_METHODDEF
    OS_SCANDIR_METHODDEF
#ifdef __MVS__
    {"chattr",          posix_chattr,    METH_VARARGS, posix_chattr__doc__},
    {"zos_system_call", os_zos_system_call, METH_VARARGS, os_zos_system_call__doc__},
#endif
    {NULL,              NULL}            /* Sentinel */
};

static int
all_ins(PyObject *m)
{
#ifdef __MVS__
    if (PyModule_AddIntMacro(m, SYSTEM_CALL__SVC)) return -1;
    if (PyModule_AddIntMacro(m, SYSTEM_CALL__PC)) return -1;
    if (PyModule_AddIntMacro(m, SYSTEM_CALL__CALL)) return -1;
    if (PyModule_AddIntMacro(m, SYSTEM_CALL__CALL31)) return -1;
#endif
    return 0;
}


#define INITFUNC PyInit__posix
#define MODNAME "_posix"

static struct PyModuleDef posixmodule = {
    PyModuleDef_HEAD_INIT,
    MODNAME,
    posix__doc__,
    -1,
    posix_methods,
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

    m = PyModule_Create(&posixmodule);
    if (m == NULL)
        return NULL;

    /* Initialize environ dictionary */
    v = convertenviron();
    Py_XINCREF(v);
    if (v == NULL || PyModule_AddObject(m, "environ", v) != 0)
        return NULL;
    Py_DECREF(v);

    if (all_ins(m))
        return NULL;

    if (setup_confname_tables(m))
        return NULL;

    Py_INCREF(PyExc_OSError);
    PyModule_AddObject(m, "error", PyExc_OSError);

    Py_INCREF((PyObject*) StatResultType);
    PyModule_AddObject(m, "stat_result", (PyObject*) StatResultType);

    /* suppress "function not used" warnings */
    {
    int ignored;
    fd_specified("", -1);
    follow_symlinks_specified("", 1);
    dir_fd_and_follow_symlinks_invalid("chmod", DEFAULT_DIR_FD, 1);
    dir_fd_converter(Py_None, &ignored);
    dir_fd_unavailable(Py_None, &ignored);
    }

    /*
     * provide list of locally available functions
     * so os.py can populate support_* lists
     */

    Py_INCREF((PyObject *) &DirEntryType);
    PyModule_AddObject(m, "DirEntry", (PyObject *)&DirEntryType);

    initialized = 1;

    return m;
}

#ifdef __cplusplus
}
#endif
