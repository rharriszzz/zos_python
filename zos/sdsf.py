from zos.dynalloc import dynalloc, dynunalloc
ORDONLY   = 0x00000002
OWRONLY   = 0x00000001
from zos.load import load
from os import pipe
from zos._system_call import zos_system_call, SYSTEM_CALL__CALL31
from threading import Thread

class sdsf(Thread):
    lines, columns = (60, 132)

    isfout_r_fd, isfout_w_fd = os.pipe()
    isfin_r_fd, isfin_w_fd = os.pipe()

    flags = fcntl.fcntl(isfout_r_fd, fcntl.F_GETFL)
    fcntl.fcntl(isfout_r_fdd, fcntl.F_SETFL, flags | os.O_NONBLOCK)

    def run(self):
        ISFAFD = load('ISFAFD')
        rc, results = dynalloc({"DDNAME":"ISFOUT",
                                "PATH":"/dev/fd%d" % isfout_w_fd,
                                "PATH_OPTIONS": OWRONLY,
                                "FILE_DATA_ORGANIZATION":"NL",
                                "LRECL":columns+1,
                                "RECFM":"FBA",
                                "BLKSIZE":columns+1})
        rc, results = dynalloc({"DDNAME":"ISFIN",
                                "PATH":"/dev/fd%d" % isfin_r_fd,
                                "PATH_OPTIONS": ORDONLY,
                                "FILE_DATA_ORGANIZATION":"NL",
                                "LRECL":80,
                                "RECFM":"FB",
                                "BLKSIZE":80})
        ISFAFD_args = "++%d,%d" % (lines, columns)
        ISFAFD_call = bytearray_set_address_size(bytearray(2+len(ISFAFD_args)), 31)
        struct.pack_into('Hs', ISFAFD_call, 0,
                         len(ISFAFD_args), ISFAFD_args)

        save_area = bytearray_set_address_size(bytearray(18*4), 31)
        call_args = bytearray(5*8)
        struct.pack_into('QQQQQ', call_args, 0,
                         ISFAFD, 0, bytearray_buffer_address(ISFAFD_call), bytearray_buffer_address(save_area), SYSTEM_CALL__CALL31)
        zos_system_call(call_args)
        ISFAFD_rc = struct.unpack_from('Q', call_args, 0)[0]

        rc, results = dynunalloc({"DDNAME":"ISFIN"})
        rc, results = dynunalloc({"DDNAME":"ISFOUT"})

    def command(self, command, timeout=0.1):
        # read any pending output
        # write the command
        # read all input, until we block and then timeout is reached
        pass
    
    def close(self):
        # flush and close isfin_w_fd
        # read everything from isfout_r_fd, then close it

"""
//SDSFJOB JOB
// EXEC PGM=ISFAFD,PARM='++lines,columns'
//ISFOUT DD SYSOUT=*
//ISFIN DD *
log
/d his
/s his
/d his
/*
//
"""
