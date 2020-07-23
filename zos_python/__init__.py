import codecs
cp1047_oe = 'cp1047_oe'
try:
    codecs.lookup(cp1047_oe)
except LookupError:
    cp1047_oe = 'cp1047'

if hasattr(bytearray, 'set_address_size'):
    def bytearray_set_address_size(ba, size):
        return ba.set_address_size(size)
    def bytearray_buffer_address(ba):
        return ba.buffer_address()
else:
    from .builtins._bytearray import bytearray_set_address_size, bytearray_buffer_address

import os
if not hasattr(os, 'zos_system_call'):
    import zos_python.builtins._system_call
    for name in ('zos_system_call','SYSTEM_CALL__SVC','SYSTEM_CALL__PC','SYSTEM_CALL__CALL','SYSTEM_CALL__CALL31'):
        setattr(os, name, getattr(zos_python.builtins._system_call, name))
        setattr(__module__, name, getattr(zos_python.builtins._system_call, name))

import fcntl
if not hasattr(fcntl, 'F_SETTAG'):
    import zos_python.builtins._fcntl
    for name in ('F_SETTAG','FT_UNTAGGED','FT_BINARY','F_CONTROL_CVT',
                 'SETCVTOFF','SETCVTON','SETAUTOCVTON','QUERYCVT',
                 'SETCVTALL','SETAUTOCVTALL'):
        setattr(fcntl, name, getattr(zos_python.builtins._fcntl, name))
        setattr(__module__, name, getattr(zos_python.builtins._system_call, name))

if False: # not ready yet
    if not hasattr(os.stat("/"), 'st_ft_ccsid'):
        import zos_python.builtins._posix
        os.stat = zos_python.builtins._posix.stat
        # also lstat, fstat, scandir, chattr, uname
        
