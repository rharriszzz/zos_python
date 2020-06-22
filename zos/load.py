
import struct
import os
import codecs

abend_code_offset = 0
abend_exit_offset = abend_code_offset + 4
exit_list_offset = abend_exit_offset + 17*2
dcb_offset = exit_list_offset + 1*4
a24_size = dcb_offset + 0x58

class load_from_ddname_and_name():
    ddname = None
    name = None
    ep = None
    verbose = False
    
    def __init__(self, ddname, name, verbose=False):
        self.ddname = ddname
        self.name = name
        self.verbose = verbose
        self.svc_args = bytearray(5*8)
        self.build_a24(ddname)
        self.open()
        try:
            self.bldl(name)
            self.load()
        finally:            
            self.close()
        
    def build_a24(self, ddname):
        self.a24 = bytearray(a24_size).set_address_size(24)
        struct.pack_into('HHHHHHHHHHHHHHHHH', self.a24, abend_exit_offset,
                             0x5870, 0x1004, # L   R7,4(,R1)   # R7 is the DCB 
                             0x9104, 0x1003, # TM  3(R1),X'04' # is it ignorable?
                             0x4770, 0xF012, # BNZ *+10
                             0x9200, 0x1003, # MVI 3(R1),X'00' # if we can't ignore, allow it to abend
                             0x07FE,         # BR R14          # return
                             0x9204, 0x1003, # MVI 3(R1),X'04' # ignore it
                             0xA77A, 0xFFFF & -dcb_offset, # AHI R7,xxxx
                             0xD203, 0x7000, 0x1000, # MVC 0(R7),0(R1)
                             0x07FE)         # BR R14          # return

        struct.pack_into('I', self.a24, exit_list_offset,
                            ((0x80 + 0x11)<<24) + (self.a24.buffer_address() + abend_exit_offset))

        # DCB DSORG=PO,MACRF=R
        for i in (0x17, 0x1F, 0x23, 0x37, 0x3B, 0x47, 0x4B, 0x4F, 0x57):
            self.a24[dcb_offset + i] = 0x01
        self.a24[dcb_offset + 0x1A] = 0x02
        self.a24[dcb_offset + 0x30] = 0x02
        self.a24[dcb_offset + 0x32] = 0x24
        struct.pack_into("8s", self.a24, dcb_offset + 0x28,
                            codecs.encode("{:8s}".format(ddname), encoding='cp1047_oe'))
        exit_list_address = bytearray(4)
        struct.pack_into('I', exit_list_address, 0,
                         self.a24.buffer_address() + exit_list_offset)
        struct.pack_into("3s", self.a24, dcb_offset + 0x35,
                         exit_list_address[1:])

    def open(self):
        # OPEN (dcb,(INPUT)),MODE=31
        open_args = bytearray(8).set_address_size(31)
        struct.pack_into('=B3xI', open_args, 0,
                            0x80, self.a24.buffer_address() + dcb_offset)
        struct.pack_into('QQQQQ', self.svc_args, 0,
                         0, open_args.buffer_address(), 0,
                         19, os.SYSTEM_CALL__SVC) 
        os.zos_system_call(self.svc_args)
        rc = struct.unpack_from('7xB', self.svc_args, 0)[0]
        if rc > 4:
            abend_code = struct.unpack_from('I', self.a24, 0)[0]
            if abend_code:
                raise OSError("OPEN abend %X" % abend_code)
            else:
                raise OSError("OPEN failed, rc=%X" % rc)
        # dcb + 0x30  is bit 0x10 on?  DCB_OPEN_FLAGS_OPN

    def bldl(self, name):
        # BLDL bldl_list,dcb
        self.bldl_list = bytearray(72).set_address_size(31)
        struct.pack_into('=HH8s', self.bldl_list, 0,
                            1, 68, codecs.encode("{:8s}".format(name), encoding='cp1047_oe') )
        if self.verbose:
            print(["%08X" % v for v in struct.unpack_from('III', self.bldl_list, 0)])
        struct.pack_into('QQQQQ', self.svc_args, 0,
                         0, self.bldl_list.buffer_address(), self.a24.buffer_address() + dcb_offset,
                         18, os.SYSTEM_CALL__SVC) 
        os.zos_system_call(self.svc_args)
        rc, reason = struct.unpack_from('7xB7xB', self.svc_args, 0)
        if rc > 0:
            raise OSError("BLDL failed for %s, rc=%X, reason=%X" % (self.name, rc, reason))

    def load(self):
        # LOAD DE=bldl_list,DCB=dcb,ERRRET=NEXT
        struct.pack_into('QQQQQ', self.svc_args, 0,
                         0, self.bldl_list.buffer_address()+4, 0x80000000 + (self.a24.buffer_address() + dcb_offset),
                         8, os.SYSTEM_CALL__SVC) 
        os.zos_system_call(self.svc_args)
        #unsigned int r15; /* good:0                         bad:returnCode */
        #unsigned int r0;  /* good:ep_including_amode        bad:n/a  */
        #unsigned int r1;  /* good:apf+length_in_doublewords bad:reasonCode */
        codes = struct.unpack_from("4xI8x4xI", self.svc_args, 0) # ignore the high order 32 bits
        if codes[0] == 0:
            self.ep = struct.unpack_from("4xI", self.svc_args, 1*8)[0]
        else:
            raise OSError("LOAD return_code=%X, reason_code=%X" % codes)
        
    def close(self):
        # CLOSE (MYDCB),MODE=31
        close_args = bytearray(8).set_address_size(31)
        struct.pack_into('=B3xI', close_args, 0,
                            0x80, self.a24.buffer_address() + dcb_offset)
        struct.pack_into('QQQQQ', self.svc_args, 0,
                         0, close_args.buffer_address(), 0,
                         20, os.SYSTEM_CALL__SVC) 
        os.zos_system_call(self.svc_args)
        rc = struct.unpack_from('Q', self.svc_args, 0)


import zos.dynalloc
def load_from_dataset(dsname, module_name, verbose=False):
    rc, results = zos.dynalloc.dynalloc({"DSNAME":dsname, "STATUS":"SHR", "DDNAME_RETURN":None})
    if verbose:
        print("rc=%X, results=%r" % (rc, results))
    ddname = results['DDNAME_RETURN']
    info = load_from_ddname_and_name(ddname, module_name, verbose=verbose)
    if verbose:
        print("%s=%08X" % (info.name, info.ep))
    rc, results = zos.dynalloc.dynunalloc({"DDNAME":ddname})
    return info.ep


def load(name):
    name_buffer = bytearray(8).set_address_size(31)
    struct.pack_into("8s", name_buffer, 0, codecs.encode("{:8s}".format(name), encoding='cp1047_oe'))
    
    load_params = bytearray(3*4).set_address_size(31)
    struct.pack_into('IIBBBB', load_params, 0,
                     name_buffer.buffer_address(), 0, 0, 0, 0x20, 0)

    svc_args = bytearray(5*8)
    struct.pack_into('QQQQQ', svc_args, 0,
                     9, 0, load_params.buffer_address(),
                     122, os.SYSTEM_CALL__SVC)

    os.zos_system_call(svc_args)
    
    #unsigned int r15; /* good:0                         bad:returnCode */
    #unsigned int r0;  /* good:ep_including_amode        bad:n/a  */
    #unsigned int r1;  /* good:apf+length_in_doublewords bad:reasonCode */
    codes = struct.unpack_from("4xI8x4xI", svc_args, 0) # ignore the high order 32 bits
    if codes[0] == 0:
        return struct.unpack_from("4xI", svc_args, 1*8)[0]
    else:
        raise OSError("LOAD return_code=%X, reason_code=%X" % codes)

