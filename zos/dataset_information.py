from zos._bytearray import *
from zos._system_call import *

import ctypes

def dump_region(address, size):
    result = "address=%016X, size=%016X\n" % (address, size)
    for addr in range(address, address+size, 32):
        if addr > address and ((addr-address) % 8) == 0:
            result+="\n"
        if addr == address or ((addr-address) % 8) == 0:
            result += "%04X  " % (addr - address)
        for addr1 in range(addr, addr+32, 4):
            result+="%08X " % (ctypes.c_uint.from_address(addr1).value,)
    return result

import codecs
cp1047_oe = 'cp1047_oe'
try:
    codecs.lookup(cp1047_oe)
except LookupError:
    cp1047_oe = 'cp1047'
from datetime import date
import os
import struct
import sys

dscb1_fmt = (#('dsname', '44s'),
             ('fmtid', '1s'),
             ('dssn', '6s'), # identifies the first volume
             ('volseq', 'H'),
             ('creation_date', 'BH', 'date'),
             ('expiration_date', 'BH', 'date'),
             ('number_of_extents', 'B'),
             ('nobdb', 'B'), # pds only
             ('flag1', 'B',
                  ('compressable', 'checkpointed', None, 'recalled', 'large', None, 'eattr=opt', 'eattr=no')),
             (None, '13s'), # 'system_code' is always 'IBMOSVS2'
             ('last_referenced_date', 'BH', 'date'),
             ('sms_flag', 'B',
                  ('system_managed', 'no_bcs_entry', 'may_reblock', 'blocksize_from_create',
                   'pdse_ds', 'extended_format_ds', 'hfs_ds', 'extended_attributes')),
             ('secondary_space_extension_flag', 'B', ('block', 'mb', 'kb', 'b', '2**8', '2**16')),
             ('secondary_space_extension_value', 'H'),
             ('dsorg_flag', 'H', ('IS', 'PS', 'D', 'T', None, None, 'PO', 'U',  'G', None, None, None, 'V')),
             ('recfm', 'B',
                  ('F_or_U', 'V_or_U', None, 'B',  'S', 'A', 'M', None)),
             ('option', 'B',
                  ('Write validity check', 'Allow data check', 'Chained scheduling', 'VSE/MVS interchange feature on tape',
                   'Treat EOF as EOV (tape)', 'Search direct', 'User label totaling', 'Each record contains a table reference character'),
                  (None, 'ICFC')), # if VSAM
             ('block_size', 'H'),
             ('lrecl', 'H'),
             ('key_length', 'B'),
             ('relative_key_position', 'H'),
             ('data_set_indicators', 'B',
                  ('last volume containing data', 'RACF with a discrete profile', 'block length is a multiple of 8 bytes', 'password required',
                   'modified since last recall', 'password not required to read',
                   'data set opened for other than input since last backup copy made', 'secure checkpoint data set')),
             ('secondard_allocation_flag', 'B',
                 ('CYL_or_TRK', 'AVG_or_TRK', None, 'EXT', 'CONTIG', 'MXIG', 'ALX', 'ROUND')),
             ('secondary_allocation_quantity', '3s', 'integer'),
             ('last_used_track_and_record', '3s', 'integer'),
             ('track_balance', 'H'), # if extended, high order of previous field, otherwise remaining space on last track
             (None, 'B'),
             ('ttt_high', 'B')) # if large, high order of last_used_track_and_record 

def unpack_from_format(data, offset, fmt, debug=False):
    values_list = list(struct.unpack_from('='+''.join([e[1] for e in fmt]), data, offset))
    result = {}
    for name, fmt, *rest in fmt:
        if debug:
            print("name=%s, value=%r" % (name, values_list[0]))
        if name is None:
            values_list.pop(0)
            continue
        if len(rest) > 0 and rest[0] == 'date':
            year = 1900 + values_list.pop(0)
            day_number = values_list.pop(0)
            if year == 1900:
                continue
            value = date.fromordinal(date(year, 1, 1).toordinal() + day_number - 1)
        elif len(rest) > 0 and rest[0] == 'integer':
            value = int.from_bytes(values_list.pop(0), byteorder='big', signed=False)
        elif len(rest) > 0:
            fields = rest[0]
            value_int = values_list.pop(0)
            value = set()
            size = 8 if fmt == 'B' else 16
            for field_pos, field_name in enumerate(fields):
                if value_int & (1 << (size - 1 - field_pos)):
                    value.add(field_name)
        elif 's' in fmt: 
            value = str.rstrip(codecs.decode(values_list.pop(0), cp1047_oe))
        else:
            value = values_list.pop(0)
        if value:
            result[name] = value
    return result

def volser_from_dsname(dsname, svc_args=None, encoding=None):
    if svc_args is None:
        svc_args = bytearray(5*8)
    if encoding is None:
        dsname = codecs.encode("{:44s}".format(dsname), encoding=cp1047_oe)
    locate = bytearray_set_address_size(bytearray(4+4+4+4 + 44+4 + 265), 31)
    struct.pack_into('=IIII' + '44s', locate, 0,
                     0x44000000, bytearray_buffer_address(locate)+4*4, 0, bytearray_buffer_address(locate)+4*4+44+4,
                     dsname)
    struct.pack_into('QQQQQ', svc_args, 0,
                     0, 0, bytearray_buffer_address(locate),
                     26, SYSTEM_CALL__SVC) # LOCATE
    zos_system_call(svc_args)
    rc = struct.unpack_from('=4xI', svc_args, 0)[0]
    if rc != 0:
        raise OSError("LOCATE NAME returned rc=0x%X" % (rc,))
    volser = struct.unpack_from('6s', locate, 4*4+44+4 + 2+4)[0]
    if encoding is None:
        volser = codecs.decode(volser_ebcdic, cp1047_oe)
    locate = None
    return volser
        
def dscb1data_from_dsname_and_volser(dsname, volser, debug=False, svc_args=None, encoding=None):
    if svc_args is None:
        svc_args = bytearray(5*8)
    if encoding is None:
        dsname = codecs.encode("{:44s}".format(dsname), encoding=cp1047_oe)
        volser = codecs.encode("{:6s}".format(volser), encoding=cp1047_oe)
    obtain_search = bytearray_set_address_size(bytearray(4+4+4+4 + 44+6+140), 31)
    struct.pack_into('=IIII' + '44s6s', obtain_search, 0,
                     0xC1000000 + 0x801, # CAMLST_SEARCH + CAMLST_EADSCB_OK
                     bytearray_buffer_address(obtain_search)+4*4,    
                     bytearray_buffer_address(obtain_search)+4*4+44,
                     bytearray_buffer_address(obtain_search)+4*4+44+6,
                     dsname, volser)
    struct.pack_into('QQQQQ', svc_args, 0,
                     0, 0, bytearray_buffer_address(obtain_search),
                     27, SYSTEM_CALL__SVC) # CAMLST OBTAIN
    zos_system_call(svc_args)
    rc = struct.unpack_from('=4xI', svc_args, 0)[0]
    if rc != 0:
        raise OSError("CAMLIST SEARCH returned rc=0x%X" % (rc,))
    if debug:
        print(dump_region(bytearray_buffer_address(obtain_search)+4*4+44+6, 140))
    return (obtain_search, 4*4+44+6)

def get_dscb1(dsname, volser=None, debug=False):
    dsname = codecs.encode("{:44s}".format(dsname), encoding=cp1047_oe)
    svc_args = bytearray(5*8)
    if volser:
        volser = codecs.encode("{:6s}".format(volser), encoding=cp1047_oe)
    else:
        volser = volser_from_dsname(dsname, svc_args, cp1047_oe)
    if debug:
        print("volser=%s" % str.rstrip(codecs.decode(volser, cp1047_oe)))

    dscb1data, dscb1offset = dscb1data_from_dsname_and_volser(dsname, volser,
                                                              debug=debug, svc_args=svc_args, encoding=cp1047_oe)

    return unpack_from_format(dscb1data, dscb1offset, dscb1_fmt, debug=debug)
                       
if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print("Usage: python dataset-information.py dsname [volser]")
    else:
        if len(sys.argv) > 2:
            volser = sys.argv[2]
        else:
            volser = None
        for name, value in get_dscb1(sys.argv[1], volser).items():
            print("%s=%r" % (name, value))
