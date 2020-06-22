import codecs
import ctypes
import os
import struct
import sys
from datetime import datetime, timedelta
from zos.dynalloc import dynalloc

def dump_region(address, size, show_header=True, show_address=True):
    if show_header:
        result = "address=%016X, size=%016X\n" % (address, size)
    else:
        result = ""
    for addr in range(address, address+size):
        if show_address:
            if addr > address and (addr % 8) == 0:
                result+="\n"
            if addr == address or (addr % 8) == 0:
                result += "%04X  " % (addr - address)
        result+="%02X " % (ctypes.c_ubyte.from_address(addr).value,)
    return result

phases = {
    # code: (JES3 name, JES2 name)
    1: ('No subchain exists', None),
    2: ('Active in CI in an FSS address space', None),
    3: ('Awaiting postscan (batch)', None),
    4: ('Awaiting postscan (demsel)', None),
    5: ('Awaiting volume fetch', None),
    6: ('Awaiting start setup', 'JES2 awaiting setup'),
    7: ('Awaiting/active in MDS system select processing', None),
    8: ('Awaiting resource allocation', None),
    9: ('Awaiting unavailable VOL(s)', None),
    10: ('Awaiting volume mounts', None),
    11: ('Awaiting/active in MDS system verify processing', None),
    12: ('Error during MDS processing', None),
    13: ('Awaiting selection on main', 'Awaiting execution'),
    14: ('Scheduled on main', 'Actively executing'),
    17: ('Awaiting breakdown', 'Active in output'),
    18: ('Awaiting MDS restart proc.', None),
    19: ('Main and MDS proc. complete', None),
    20: ('Awaiting output service', 'Awaiting hardcopy'),
    21: ('Awaiting output service WTR', None),
    22: ('Awaiting rsvd services', None),
    23: ('Output service complete', None),
    24: ('Awaiting selection on main (demand select job)', None),
    25: ('Ending function rq waiting or i/o completion', None),
    26: ('Ending function rq not Processed', None),
    27: ('Maximum rq index value', None),
    128: (None, 'Active in input processing'),
    129: (None, 'Awaiting conversion'),
    130: (None, 'Active in conversion'),
    131: (None, 'Active in SETUP'),
    132: (None, 'Active in spin'),
    133: (None, 'Awaiting output'),
    134: (None, 'Awaiting purge'),
    135: (None, 'Active in purge'),
    136: (None, 'Active on NJE sysout receiver'),
    137: (None, 'Awaiting NJE transmission'),
    138: (None, 'Active on NJE Job transmitter'),
    # phases used only for selection
    # 253: 'Job has not completed execution'
    # 254: 'job has completed execution'
    }
    
completion_type_codes = (
    'No completion info',
    'Job ended normally',
    'Job ended by CC',
    'Job had a JCL error',
    'Job was canceled',
    'Job ABENDed',
    'Converter ABENDed',
    'Security error',
    'Job failed in EOM',
    'Converter error',
    'System failure',
    'Job has been flushed')

def identity(x):
    return x

def value_name_from_dict_fn(value_to_name_dict):
    return lambda x: value_to_name_dict[x]

def bit_names_name_from_list_fn(bit_to_name_list, byte_count):
    def decode_bits(x):
        result = []
        for i, name in enumerate(bit_to_name_list, start=1):
            if x & (1<<(byte_count*8-i)):
                result.append(name)
        return tuple(result)
    return decode_bits

def convert_from_ebcdic(x):
    return codecs.decode(x, 'cp1047_oe').rstrip()

def convert_from_ebcdic_for_CHARS(x):
    s = codecs.decode(x, 'cp1047_oe')
    return (s[0:4].rstrip(), s[4:8].rstrip(), s[8:12].rstrip(), s[12:16].rstrip())

# F time hundredths of seconds since midnight; date 0cyydddF
def time_cyydddf(x):
    year = 1900 + ((x >> 24) & 0xF)*100 + ((x >> 20) & 0xF)*10 + ((x >> 16) & 0xF)*1
    day_number = ((x>>12)&0x0F)*100 + ((x>>8)&0x0F)*10 + ((x>>8)&0x0F)*1
    seconds = (x>>32)*0.01
    return datetime(year, 1, 1) + timedelta(days=day_number-1, seconds=seconds)

def stck4_timedate(x):
    return datetime(1900, 1, 1) + timedelta(seconds=x*(1<<20)*1e-6)

def maxrc(x):
    completion_type = completion_type_codes[(x>>24)&0xF]
    abend_or_completion_code = x & 0xFFFFFF
    if x & 0x80000000: # abend code
        if abend_or_completion_code & 0xFFF000:
            return (completion_type, "S3X" & abend_or_completion_code>>12)
        else:
            return (completion_type, "U4d" % abend_or_completion_code)
    elif x & 0x40000000: # completion code
        return (completion_type, "rc=%d" % abend_or_completion_code)
    else:
        return (completion_type, "")

def decode_recfm(x):
    return (("", "V", "F", "U")[x>>6])+\
        ("B" if x&0x10 else "")+\
        ("S" if x&0x08 else "")+\
        (("", "M", "A", "")[(x>>1)&0x3])

def decode_phase(x):
    jes3_name, jes2_name = phases[x]
    return jes2_name

# returns a list of (name, ctype, offset, convert, size)
def field_information (offset, struct_type, name, *extra_info):
    size = 0
    if struct_type == '4s4s4s4s':
        return (name, ctypes.c_char * 16, offset, convert_from_ebcdic_for_CHARS, 16)
    elif struct_type == 'BBBBBBBB':
        return (name, ctypes.c_ubyte * 8, offset, identity, 8)
    elif struct_type == 'B':
        if extra_info and isinstance(extra_info[0], dict):
            return (name, ctypes.c_ubyte, offset, value_name_from_dict_fn(extra_info[0]), 1)
        elif extra_info and isinstance(extra_info[0], tuple):
            return (name, ctypes.c_ubyte, offset, bit_names_name_from_list_fn(extra_info[0], 1), 1)
        elif extra_info and extra_info[0] == 'recfm':
            return (name, ctypes.c_ubyte, offset, decode_recfm, 1)
        elif extra_info and extra_info[0] == 'phase':
            return (name, ctypes.c_ubyte, offset, decode_phase, 1)
        else:
            return (name, ctypes.c_ubyte, offset, identity, 1)
    elif struct_type == 'H':
        return (name, ctypes.c_ushort, offset, identity, 2)
    elif struct_type == 'I':
        if extra_info and extra_info[0] == 'maxrc':
            return (name, ctypes.c_uint, offset, maxrc, 4)
        elif extra_info and extra_info[0] == 'stck4':
            return (name, ctypes.c_uint, offset, stck4_timedate, 4)
        else:
            return (name, ctypes.c_uint, offset, identity, 4)
    elif struct_type == 'Q':
        if extra_info and extra_info[0] == 'time_cyydddf':
            return (name, ctypes.c_ulong, offset, time_cyydddf, 8)
        else:
            return (name, ctypes.c_ulong, offset, identity, 8)
    elif 'x' == struct_type[-1]:
        return (None, None, offset, None, int(struct_type[:-1]))
    elif 's' == struct_type[-1]:
        length = int(struct_type[:-1])
        if extra_info and extra_info[0] == 'binary':
            return (name, None, offset, None, length)
        elif extra_info and extra_info[0] == 'tuple':
            return (name, ctypes.c_char * length, offset, tuple, length)
        else:
            return (name, ctypes.c_char * length, offset, convert_from_ebcdic, length)
    else:
        raise Exception("Failed to recognize struct_type %r" % struct_type)

def field_information_list(*fields):
    offset = 0
    result = []
    for field in fields:
        info = field_information(offset, *field)
        result.append(info)
        offset += info[4]
    return result
    
structure_info = {
    0x0100:field_information_list( # Job level terse section
                 ('8s', 'job name'),      
                 ('8s', 'job identifier'),
                 ('8s', 'original job identifier'),
                 ('8s', 'job class'),
                 ('8s', 'origin node'),
                 ('8s', 'execution node'),
                 ('8s', 'default print node'),
                 ('8s', 'default print remote name'),
                 ('8s', 'default punch node'),
                 ('8s', 'default punch remote name'),
                 ('8s', 'owner userid'),
                 ('8s', 'seclabel'),
                 ('8s', 'MVS system on which the job is active'),
                 ('8s', 'JES2 member on which the job is active'),
                 ('18s', 'Name of device job is active on'),
                 ('B', 'Phase job is in', 'phase'),
                 ('B', 'hold', {1:'no', 2:'yes', 3:'yes, duplicate job name'}),
                 ('B', 'type', {1:'STC', 2:'TSU', 3:'JOB', 4:'APPC', 5:'JOBGROUP'}),
                 ('B', 'priority'),
                 ('B', 'ARM status', ('ARM registered', 'awaiting ARM restart')),
                 ('B', 'indicators', ('JESLOG is spinable', 'JOB is being processed for End of Memory', 'JESJCLIN dataset avail', 'MVS SYSLOG job', 'NJE job flagged dubious')),
                 ('I', 'job completion', 'maxrc'),
                 ('I', 'Position of job on class queue or phase queue'),
                 ('I', 'Binary job number'),
                 ('8s', 'Percent SPOOL utilization'),
                 ('8s', 'SYSLOG MVS system name'),
                 ('64s', 'job correlator'),
                 ('I', 'number of track groups on spool')),
    0x0200:(# JES2 Terse section type
                ),
    0x0300:(# Affinity section type
                ),
    0x0400:(# Scheduling section, modifier=0
                ),
    0x0401:(# Scheduling section, modifier=1
                ),
    0x0402:(# Scheduling section, modifier=2
                ),
    0x0500:(# SECLABEL affinity section
                ),
    0x0600:(# JES3 Terse section type
                ),
    0x0400:(# Scheduling section, 3 modifiers
                ),
    0x0500:(# SECLABEL affinity section
                ),
    0x0600:(# JES3 Terse section type
                ),
    0x0700:(# JES2 Job Zone Dependency Network section type (see STATJZDN).
                ),
    0x0A00:(# JES2 Dynamic Dependency information terse section - (see STATDYND).
                ),
    0x0B00:(# JES2 NET (DJC) information terse section - (see STATNETI)
                ),

    0x0800:(# JES2 Job Dependency Block (STATDB) - First header section type (see STATDBHD).
                ),
    0x0900:(# JES2 Job Dependency Block (STATDB) - Terse section type (see STATDBTE).
                ),

    #20 First job verbose section
    0x2100:field_information_list(# Job level verbose section
                ('B', 'section flag', ('Error obtaining verbose data')),
                ('B', None),
                ('H', 'job copy count'),
                ('H', 'job lines per page'),
                ('18s', 'Input device name'),
                ('8s', 'Input system/member'),
                ('I', 'job input count'),
                ('I', 'job line count'),
                ('I', 'job page count'),
                ('I', 'job output count'), 
                ('Q', 'input start', 'time_cyydddf'), # time 'I' hundredths of seconds since midnight, date 0cyydddF
                ('Q', 'input end', 'time_cyydddf'), # time 'I' hundredths of seconds since midnight, date 0cyydddF
                ('8s', 'execution MVS system name'),
                ('8s', 'execution JES2 member name'),
                ('Q', 'execution start', 'time_cyydddf'), # time 'I' hundredths of seconds since midnight, date 0cyydddF
                ('Q', 'execution end', 'time_cyydddf'), # time 'I' hundredths of seconds since midnight, date 0cyydddF
                ('8s', 'JMRUSEID'),
                ('8s', 'message class'),
                ('8s', 'Notify Node'),
                ('8s', 'Notify Userid'),
                ('20s', 'Programmer name'),
                ('8s', 'Account number'),
                ('8s', 'NJE department'),
                ('8s', 'NJE building'),
                ('8s', 'Job card room number'),
                ('8s', 'JDVT name for job'),
                ('8s', 'Submitting userid'),
                ('8s', 'Submitting group'),
                ('H', 'Max LRECL of JCLIN stream'),
                ('B', 'job suppression', ('Suppress EVENTLOG SMF record')),
                ('B', 'feature suppression', ('Suppress EVENTLOG writes', 'Suppress non-printable data sets on NJE')),
                ('4s', 'job completion', 'maxrc'),
                ('8s', 'net account'),
                ),
    0x2200:(# JES2 verbose section type
            ),
    0x2300:(# JES3 verbose section type
            ),
    0x2400:(# Security section
            ),
    0x2500:(# Accounting section
            ),
    #40 First SYSOUT section type
    0x4100:field_information_list(# SYSOUT level terse section
                ('8s', 'owner'),
                ('8s', 'seclabel'),
                ('18s', 'destination'),
                ('8s', 'class'),
                ('I', 'record count'),
                ('I', 'page count'),
                ('I', 'line count'),
                ('Q', 'byte count'), # JES3
                ('8s', 'forms'),
                ('8s', 'fcb'),
                ('8s', 'ucs'),
                ('8s', 'external writer name'),
                ('8s', 'processing mode'),
                ('8s', 'flash'),
                ('4s4s4s4s', 'printer translate table'),
                ('4s', 'MODIFY=(modname)'),
                ('B', 'MODIFY=(,trc)'),
                ('B', 'flag', ('client token is not usable', 'demand select')),
                ('2x', None),
                ('8s', 'MVS system on which the SYSOUT is active'),
                ('8s', 'JES member on which the SYSOUT is active'),
                ('18s', 'Name of device on which the SYSOUT is active (blanks if not active)'),
                ('B', 'SYSOUT hold state', ('operator command', 'HOLD=YES on the DD', 'system hold', 'TSO', 'external writer', 'BDT queue', 'TCP queue')),
                ('B', 'system hold reason'), # see IAZOHLD
                ('B', 'output disposition', ('OUTDISP=HOLD', 'OUTDISP=LEAVE', 'OUTDISP=WRITE', 'OUTDISP=KEEP')),
                ('B', 'flag1', ('BURST=YES', '3540 held data set', 'Destination has an IPADDR', 'Schedulable element has page mode data', 
                                    None, None, 'SYSOUT has job level information', 'When SYSOUT was allocated the DALRTCTK key specified')),
                ('B', 'priority'),
                ('44s', 'sysout identifier'),
                ('80s', 'client token', 'binary'),
                ('I', 'current line active on device'),
                ('I', 'current page active on device'),
                ),
    0x4200:(# JES2 SYSOUT section
            ),
    0x4300:(# JES3 SYSOUT section
            ),
    0x4500:(# Transaction (APPC) SYSOUT terse section
            ),
            
    #60 First SYSOUT verbose section
    0x6100:field_information_list(# SYSOUT level verbose section
                ('B', 'section flag', ('error obtaining verbose data', 'spin', 'spin-any or JESLOG spin', 'system data set', 'sysin', 'dummy', 'broadcast all ENF58 signals')),
                ('B', 'recfm', 'recfm'),
                ('8s', 'procname'),
                ('8s', 'stepname'),
                ('8s', 'ddname'),
                ('8s', None),
                ('8s', None),
                ('I', 'dataset availability', 'stck4'),
                ('I', 'segment id'),
                ('I', 'data set number'),
                ('H', 'lrecl'),
                ('I', 'line count'),
                ('I', 'record count'),
                ('Q', 'byte count'),
                ('I', 'record count'),
                ('44s', 'data set name'),
                ('B', 'copy count'),
                ('B', 'flash copy count'),
                ('B', 'flag', ('client token is not usable', 'spinnable',  'OPTCD=J')),
                ('B', 'step number'),
                ('8s', 'copy groups', 'tuple'),
                ('4x', None),
                ('80s', 'client token', 'binary'),
                ('4s4s4s4s', 'printer translate table'),
                ('4s', 'MODIFY=(modname)'),
                ('B', 'MODIFY=(,trc)'),
                ),
    0x6200:(# JES2 verbose section type
            ),
    0x6300:(# JES3 verbose section type
            ),
    0x6400:(# Security section
            ),
    0x6500:(# Transaction (APPC) SYSOUT section
            ),
    }
    
criteria_fields = {
    'jobname':('8s', 0x3E, 0x38, 0x20),
    'jobid':('8s', (0x46, 0x4E), 0x38, 0x10), # (low jobid, high jobid)
    'owner':('8s', 0x5E, 0x38, 0x04),
}

def MEM4(address, offset):
    return ctypes.c_int.from_address(address + offset).value

class extended_status:
    verbose = False
    ssreq_fn = MEM4(MEM4(MEM4(0,0x10),0x128),0x14)
    ssob_and_stat_len = 0x23C # version 10
    ssob_and_stat = bytearray(ssob_and_stat_len).set_address_size(31)
    arglist = bytearray(4).set_address_size(31)
    struct.pack_into('=I', arglist, 0, ssob_and_stat.buffer_address())
    struct.pack_into('=4sHHI4xI', ssob_and_stat, 0,
                    codecs.encode("{:4s}".format("SSOB"), encoding='cp1047_oe'), # E2E2D6C2
                    0x1C, 80, 0, ssob_and_stat.buffer_address()+0x20) # 0x1C is the SSOB length; 80 is extended status
    struct.pack_into('H4sBB5x', ssob_and_stat, 0x20,
                     0x21C, # version 10 length
                     codecs.encode("{:4s}".format("STAT"), encoding='cp1047_oe'), # E2E3C1E3
                     10, 0) # version 10, modifier 0
    struct.pack_into('B', ssob_and_stat, 0xDA, # STATOPT1
                     0x04) # Returned areas may be obtained in 64-bit storage
    save_area = bytearray(18*4).set_address_size(31)
    ssreq = bytearray(5*8)

    def call(self, request_type, criteria={}, requested_fields=None):
        self.requested_fields = requested_fields
        request_types = ('job_terse', 'job_verbose', 'close', 'sysout_terse', 'sysout_verbose', 'data_set_list')
        struct.pack_into('B', self.ssob_and_stat, 0x2C,
                         request_types.index(request_type)+1)
        for name, value in criteria.items():
            if not value:
                continue
            struct_fmt, position_list, bit_position, bit = criteria_fields[name]
            if isinstance(value, str):
                value = codecs.encode(("{:%ds}" % int(struct_fmt[:-1])).format(value), encoding='cp1047_oe')
            if isinstance(position_list, tuple):
                for position in position_list:
                    struct.pack_into(struct_fmt, self.ssob_and_stat, position, value)
            else:
                position = position_list
                struct.pack_into(struct_fmt, self.ssob_and_stat, position, value)
            self.ssob_and_stat[bit_position] |= bit
        struct.pack_into('QQQQQ', self.ssreq, 0,
                         self.ssreq_fn, 0, self.arglist.buffer_address(),
                         self.save_area.buffer_address(), os.SYSTEM_CALL__CALL31)
        os.zos_system_call(self.ssreq)
        self.ssi_return_code = struct.unpack_from('=4xI', self.ssreq, 0)[0]
        if self.ssi_return_code != 0:
            error_index = self.ssi_return_code / 4 - 1
            error_messages = ("The subsystem does not support this function.",
                              "The subsystem exists, but is not active.",
                              "The subsystem is not defined to MVS.",
                              "Invalid SSOB, SSIB or function code",
                              "The SSOB or SSIB have invalid lengths or formats",
                              "The SSI has not been initialized.")
            raise Exception(error_messages[errior_index])
        self.subsystem_return_code = struct.unpack_from('=I', self.ssob_and_stat, 0x0C)[0] # SSOBRETN
        self.version, self.reason, self.reason2 = struct.unpack_from('=BxBB', self.ssob_and_stat, 0x28) # STATVER, STATREAS, STATREA2
        if self.ssi_return_code == 4:
            raise Exception("Invalid search arguments")
        elif self.ssi_return_code == 8:
            raise Exception("Logic error, reason=0x%X" % self.reason)
        elif self.ssi_return_code == 12:
            raise Exception("Unsupported call type")
        #print(dump_region(self.ssob_and_stat.buffer_address(), len(self.ssob_and_stat)))
        return None

    def job_elements(self):
        have_64bit_results = struct.unpack_from('B', self.ssob_and_stat, 0x108)[0] & 0x40
        for self.jq64 in (True, False) if have_64bit_results else (False,):
            self.jqe_address = struct.unpack_from('Q' if self.jq64 else 'I',
                                                  self.ssob_and_stat,
                                                  0x118 if self.jq64 else 0x0F4)[0]
            if self.verbose:
                print("jq64=%r, jqe=%X" % (self.jq64, self.jqe_address))
            while self.jqe_address:
                self.subsystem_name = codecs.decode((ctypes.c_char*4)\
                                                    .from_address(self.jqe_address + 0x10).value, 'cp1047_oe')
                job = {"subsystem": self.subsystem_name}
                job = self.parse_element_information(self.jqe_address, 'job_terse', job)
                self.job_verbose_address = (ctypes.c_ulong if self.jq64 else ctypes.c_uint)\
                    .from_address(self.jqe_address + (0x30 if self.jq64 else 0x14)).value
                if self.job_verbose_address:
                    if self.verbose:
                        print("job_verbose=%X" % (self.job_verbose_address,))
                    job = self.parse_element_information(self.job_verbose_address, 'job_verbose', job)
                yield job
                self.jqe_address = (ctypes.c_ulong if self.jq64 else ctypes.c_uint)\
                    .from_address(self.jqe_address + (0x20 if self.jq64 else 0x08)).value
                if self.verbose:
                    print("jqe=%X" % (self.jqe_address,))


    def job_dependency_elements(self):
        if ctypes.c_short.from_address(self.jqe_address + 0x4).value >= 0x48:
            self.dependency_address = ctypes.c_ulong.from_address(self.jqe_address + 0x40).value
            while self.dependency_address:
                yield self.parse_element_information(self.dependency_address, 'job_dependency')
                self.dependency_address = ctypes.c_ulong.from_address(self.dependency_address + 0x8).value
        
    def sysout_terse_elements(self):
        self.sysout_terse_address = (ctypes.c_ulong if self.jq64 else ctypes.c_uint)\
            .from_address(self.jqe_address + (0x28 if self.jq64 else 0x0C)).value
        while self.sysout_terse_address:
            yield self.parse_element_information(self.sysout_terse_address, 'sysout_terse')
            self.sysout_terse_address = (ctypes.c_ulong if self.jq64 else ctypes.c_uint)\
                .from_address(self.sysout_terse_address + (0x18 if self.jq64 else 0x08)).value

    def sysout_verbose_elements(self):
        self.sysout_verbose_address = (ctypes.c_ulong if self.jq64 else ctypes.c_uint)\
            .from_address(self.sysout_terse_address + (0x28 if self.jq64 else 0x10)).value
        while self.sysout_verbose_address:
            yield self.parse_element_information(self.sysout_verbose_address, 'sysout_verbose')
            self.sysout_verbose_address = (ctypes.c_ulong if self.jq64 else ctypes.c_uint)\
                .from_address(self.sysout_verbose_address + (0x30 if self.jq64 else 0x14)).value
        
    def parse_element_information(self, header_address, header_type, result=None):
        if not result:
            result = {}
        offset = ctypes.c_ushort.from_address(header_address + 0x4).value
        total_length = ctypes.c_ushort.from_address(header_address + offset + 0x0).value
        address = header_address + offset
        offset = 4
        while offset < total_length:
            section_length = ctypes.c_ushort.from_address(address + offset + 0x0).value
            result = self.parse_information(address + offset, total_length - offset, result)
            offset += section_length
        return result

    def parse_information(self, address, remaining_length, result=None):
        if not result:
            result = {}
        type_and_modifier = ctypes.c_ushort.from_address(address + 0x2).value
        data_format = structure_info.get(type_and_modifier, ())
        if data_format:
            address += 4
            for name, ctype, offset, convert, size in data_format:
                if name and (not self.requested_fields or name in self.requested_fields):
                    if self.verbose:
                        print("%X %s %s" % (offset, name, dump_region(address + offset, size, 
                                                                      show_header=False, show_address=False)),
                              flush=True)
                    if ctype:    
                        value = convert(ctype.from_address(address + offset).value)
                    else:
                        value = bytearray(size)
                        ctypes.memmove(value.buffer_address(), address + offset, size)
                    if value:
                        result[name] = value
        return result

def allocate_spool_dataset(data_set_name=None, client_token=None, subsystem=None):
    client_token.set_address_size(31)
    rc, results = dynalloc({
        "DSNAME":data_set_name,
        "STATUS":"SHR",
        "UNAUTHORIZED_SUBSYSTER_REQUEST":subsystem,
        "BROWSE_TOKEN":(codecs.encode("BTKN", encoding='cp1047_oe'), 
                        bytes((3, 3)),
                        client_token.buffer_address().to_bytes(4, sys.byteorder) if client_token else 0,
                        0, 0, 0, 0),
        "CLOSE":None,
        "DDNAME_RETURN":None})
    if rc != 0:
        raise OSError("dynalloc returned %X" % rc)
    return results["DDNAME_RETURN"]

letters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789#$@&*()?/<>/.+-=_ '
letters_ebcdic = codecs.encode(letters, encoding='cp1047_oe')
decode_ebcdic = list(' ')*256
for c, e in zip(letters, letters_ebcdic):
    decode_ebcdic[e] = c

def show_data(data):
    for addr16 in range(0, len(data), 16):
        print("%04X  " % addr16, end='')
        for addr in range(addr16, min(addr16+16, len(data))):
            print("%02X " % data[addr], end='')
        print('  |', end ='')
        for addr in range(addr16, min(addr16+16, len(data))):
            print("%s" % decode_ebcdic[data[addr]], end='')
        print('|')

def show_spool_dataset(data_set_name=None, client_token=None, subsystem=None):
    ddname = allocate_spool_dataset(data_set_name=data_set_name, 
                                    client_token=client_token,
                                    subsystem=subsystem)
    print("--- %s ---" % data_set_name)
    if data_set_name.endswith('.EVENTLOG'):
        with open("DD:%s" % ddname, "rb", use_fopen=True) as out:
            show_data(out.read())
    elif data_set_name.endswith('.$INTTEXT'):
        with open("DD:%s" % ddname, "rb", use_fopen=True) as out:
            show_data(out.read())
    else:
        with open("DD:%s" % ddname, "rt", use_fopen=True, encoding="cp1047_oe") as out:
            print(out.read())

from zos.dynalloc_definitions import text_keyword_definitions, DALBRTKN, DALUASSR, KD_TYPE_DATA, KD_TYPE_VARCHAR
definitions = (
    (('BROWSE_TOKEN','DALBRTKN'),DALBRTKN,7,0,80,KD_TYPE_DATA),
    (('UNAUTHORIZED_SUBSYSTER_REQUEST','DALUASSR'),DALUASSR,1,0,4,KD_TYPE_VARCHAR),)
mapping = text_keyword_definitions['allocate']
for definition in definitions:
    mapping[definition[1]] = definition
    for name in definition[0]:
         mapping[name] = definition

def test_extended_status(jobid=None, jobname=None, owner=None):
    jobid_list = []
    es = extended_status()
    print('=== job_terse ===', flush=True)
    es.call('job_terse', criteria={'jobid':jobid, 'jobname':jobname, 'owner':owner}, requested_fields=('job identifier'))
    for job_element in es.job_elements():
        jobid_list.append(job_element['job identifier'])
        for name, value in job_element.items():
            print("%s=%r" % (name, value))
    es.call('close')
    print('')

    print('=== job_verbose ===', flush=True)
    for jobid in jobid_list:
        es.call('job_verbose', criteria={'jobid':jobid})
        for job_element in es.job_elements():
            for name, value in job_element.items():
                print("%s=%r" % (name, value))
        es.call('close')
    print('')

    print('=== sysout_terse ===', flush=True)
    for jobid in jobid_list:
        es.call('sysout_terse', criteria={'jobid':jobid})
        for job_element in es.job_elements():
            for name, value in job_element.items():
                print("%s=%r" % (name, value))
            for sysout_terse_element in es.sysout_terse_elements():
                print("sysout_terse_element")
                for name, value in sysout_terse_element.items():
                    print("%s=%r" % (name, value))
        es.call('close')
    print('')

    print('=== sysout_verbose ===', flush=True)
    for jobid in jobid_list:
        es.call('sysout_verbose', criteria={'jobid':jobid})
        for job_element in es.job_elements():
            for name, value in job_element.items():
                print("%s=%r" % (name, value))
            for sysout_terse_element in es.sysout_terse_elements():
                print("sysout_terse_element")
                for name, value in sysout_terse_element.items():
                    print("%s=%r" % (name, value))
                for sysout_verbose_element in es.sysout_verbose_elements():
                    print("sysout_verbose_element")
                    for name, value in sysout_verbose_element.items():
                        print("%s=%r" % (name, value))
        es.call('close')
    print('')

    print('=== data_set_list ===', flush=True)
    for jobid in jobid_list:
        es.call('data_set_list', criteria={'jobid':jobid})
        # es.verbose = True
        for job_element in es.job_elements():
            for name, value in job_element.items():
                print("%s=%r" % (name, value))
            for sysout_terse_element in es.sysout_terse_elements():
                print("sysout_terse_element")
                for name, value in sysout_terse_element.items():
                    print("%s=%r" % (name, value))
                for sysout_verbose_element in es.sysout_verbose_elements():
                    print("sysout_verbose_element")
                    for name, value in sysout_verbose_element.items():
                        print("%s=%r" % (name, value), flush=True)
                    subsystem = job_element['subsystem']
                    data_set_name = sysout_verbose_element['data set name']
                    client_token = sysout_verbose_element['client token']
                    flag = sysout_verbose_element.get('flag', ())
                    if flag and flag[0]=='client token is not usable':
                        print("==== %s %r ====" % (data_set_name, flag))
                    else:
                        show_spool_dataset(data_set_name=data_set_name,
                                           client_token=client_token, 
                                           subsystem=subsystem)
        es.call('close')
    print('')

if __name__ == '__main__':
    myjob = "//MYJOB JOB\n//STEP EXEC PGM=IEFBR14\n"
    from .submit import submit_job
    jobid_list = submit_job(myjob)
    test_extended_status(jobid=jobid_list[0])
    
