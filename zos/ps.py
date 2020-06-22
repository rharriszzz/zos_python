import ctypes, struct, os, sys, codecs
             
def MEM4(address, offset):
    return ctypes.c_int.from_address(address + offset).value

BPX1GTH_offset = 1056 # __getthent
BPX1GTH_addr = MEM4(MEM4(MEM4(MEM4(0,16),544),24),BPX1GTH_offset)

class get_thread_entity(object):
    def __init__(self, outputs,
                 pid=0, thid=0, asid=0, loginname=None):
        self.pid = pid
        self.thid = thid
        self.pgtha = self.make_pgtha(outputs, pid=pid, thid=thid,
                                     asid=asid, loginname=loginname)
        self.pgthb = self.make_pgthb()
        self.BPX1GTH_args = bytearray(7*8 + 2*8 + 5*4)
        struct.pack_into('QQQQQQQ' 'QQ' 'IIIII', self.BPX1GTH_args, 0,
                         self.BPX1GTH_args.buffer_address()+9*8+0*4, self.BPX1GTH_args.buffer_address()+7*8, 
                         self.BPX1GTH_args.buffer_address()+9*8+1*4, self.BPX1GTH_args.buffer_address()+8*8,
                         self.BPX1GTH_args.buffer_address()+9*8+2*4,
                         self.BPX1GTH_args.buffer_address()+9*8+3*4,
                         self.BPX1GTH_args.buffer_address()+9*8+4*4,
                         self.pgtha.buffer_address(), self.pgthb.buffer_address(),
                         len(self.pgtha), len(self.pgthb), 0, 0, 0)
        self.call_args = bytearray(5*8)
    
    def __iter__(self):
        return self
    
    def __next__(self):
        rc = struct.unpack_from('i', self.BPX1GTH_args, 9*8+2*4)[0]
        if rc == -1:
            raise StopIteration()
        struct.pack_into('QQQQQ', self.call_args, 0,
                         BPX1GTH_addr, 0, self.BPX1GTH_args.buffer_address(), 0, os.SYSTEM_CALL__CALL)
        os.zos_system_call(self.call_args)
        rc = struct.unpack_from('I', self.BPX1GTH_args, 9*8+2*4)[0]
        if rc == -1:
            raise StopIteration()
        self.move_next_from_pgthb_to_pgtha()
        if self.pid and self.pid != self.pgtha_pid:
            raise StopIteration()
        if self.thid and self.thid != self.pgtha_thid:
            raise StopIteration()
        return self.extract_data_from_pgthb()

    # ONLY FLAG1 BITS THREAD AND PTAG WILL BE CONSIDERED WHEN ACCESSPID=CURRENT AND ACCESSTHID=NEXT
    def make_pgtha(self, outputs, pid=0, thid=0,
                   asid=0, loginname=None):
        if loginname is None:
            loginname = bytearray(8)
        if isinstance(loginname, str):
            loginname = codecs.encode("{:8s}".format(loginname), encoding='cp1047_oe')
        if pid:
            process = 'CURRENT'
        else:
            process = 'NEXT'
        if thid:
            thread = 'CURRENT'
        else:
            thread = 'NEXT'
        pgtha_access_map = {'FIRST':0, 'CURRENT':1, 'NEXT':2, 'LAST':3}
        pgta_output_map = {'PROCESS':0x8000, 'CONTTY':0x4000, 'PATH':0x2000, 'COMMAND_SHORT':0x1000,
                           'FILE':0x0800, 'THREAD':0x0400, 'PTAG':0x0200, 'COMMAND_LONG':0x0100,
                           'THREADFAST':0x0080, 'FILEPATH':0x0040, 'SIGMASK':0x0020}
        outputs_code = 0
        for output in outputs:
            if output == 'COMMAND':
                output = 'COMMAND_LONG'
            outputs_code += pgta_output_map[output]
        pgtha = bytearray(0x1a)
        struct.pack_into("=IQBBH8sH", pgtha, 0,
                         pid, thid,
                         pgtha_access_map[process], pgtha_access_map[thread],
                         asid, loginname, # asid and loginname filters apply only when accesspid = first, next
                         outputs_code)
        return pgtha

    def make_pgthb(self):
        # The name of the fullword that contains the length of the output buffer.
        # Some requests could be satisfied by the minimum buffer size of 128 bytes;
        # whereas a request for all options of a process with maximum resources could exceed half a million bytes.
        return bytearray(0x4096)

    def move_next_from_pgthb_to_pgtha(self):
        pid, thid, process, thread = struct.unpack_from('=IQBB', self.pgthb, 4)
        self.pgtha_pid = pid
        self.pgtha_thread = thid
        struct.pack_into('=IQBB', self.pgtha, 0,
                         pid, thid, process, thread)
            
    def extract_data_from_pgthb(self):
        length_of_data = struct.unpack_from('I', self.pgthb, 0x14)
        results = struct.unpack_from('IIIIII', self.pgthb, 0x18)
        data = {}
        names = ('PROCESS', 'CONTTY', 'PATH', 'COMMAND', 'FILE', 'THREAD')
        functions = (self.extract_data_from_pgthc, self.extract_data_from_pgthd, self.extract_data_from_pgthe,
                     self.extract_data_from_pgthf, self.extract_data_from_pgthg, self.extract_data_from_pgthj)
        data_flag_map = {0xD5: 'NOTREQUESTED', 0xC1: 'OK', 0xE2:'STORAGE', 0xE5:'VAGUE', 0xE7:'NOTCONNECTED', 0x00:None}
        for i in range(6):
            result = results[i]
            data_flag = data_flag_map[result >> 24]
            offset = result & 0xFFFFFF
            if data_flag == 'NOTREQUESTED':
                pass
            elif data_flag == 'OK':
                data[names[i]] = functions[i](self.pgthb, offset, data_flag)
            else:
                data[names[i]] = {'data flag':data_flag}
        return data

    def extract_data_from_pgthx(self, pgthb, offset, data_flag, layout, names):
        data = struct.unpack_from(layout, pgthb, offset)
        result = {}
        if data_flag:
            result['data flag'] = data_flag
        for i in range(len(names)):
            result[names[i]] = data[i]
        return result

    def include_multiplier_in_memory_value(self, result, name):
        value = result[name]
        multiplier = value & 0xFF
        value_without_multiplier = value >> 8
        multiplier_map = {0:1, 0xD2: 3, 0xD4: 6, 0xC7: 9, 0xE3: 12, 0xD7: 15}
        result[name] = (value_without_multiplier, multiplier_map[multiplier])
        
    def decode_flags(self, result, name, value_map):
        value = result[name]
        names = []
        for bit_code,bit_name in value_map.items():
            if value & bit_code:
                names.append(bit_name)
        result[name] = tuple(names)
    
    def extract_data_from_pgthc(self, pgthb, offset, data_flag):
        layout = "=4x3Bx16I4H8s8sIIQQQ"
        names = ('flag1', 'flag2', 'flag3',
                 'process id', 'parent id', 'process group', 'session id', 'foreground process group',
                 'effective user id', 'real user id', 'saved set user id', 'effective group id', 'real group id',
                 'saved set group id', 'allocated user storage above 16 mb', 'count of slow-path syscalls',
                 'time spent in user code', 'time spent in system code', 'time process was dubbed',
                 'no. oe threads', 'no. pthread created threads', 'count of all threads', 'address space id',
                 'mvs job name', 'login name', 'maximum memlimit', 'memusage above 2gb', 'user cpu time',
                 'system cpu time', 'start time') # in microseconds
        result = self.extract_data_from_pgthx(pgthb, offset, data_flag, layout, names)
        if result['flag2'] & 0x80:
            self.include_multiplier_in_memory_value(result, 'maximum memlimit')
        if result['flag3'] & 0x80:
            self.include_multiplier_in_memory_value(result, 'memusage above 2gb')
        flag1_map = {0x80:"multiple processes", 0x40:"swapped", 0x20:"trace", 0x10:"stopped",
                     0x08:"incomplete", 0x04:"zombie", 0x02:"shutdown blocking", 0x01:"shutdown permanent"}
        self.decode_flags(result, 'flag1', flag1_map)
        flag2_map = {0x40:"respawnable", 0x20:"syscall trace"}
        self.decode_flags(result, 'flag2', flag2_map)
        result['mvs job name'] = str.rstrip(codecs.decode(result['mvs job name'], 'cp1047_oe'))
        result['login name'] = str.rstrip(codecs.decode(result['login name'], 'cp1047_oe'), " \x00")
        return result

    def extract_data_from_pgthx_string(self, pgthb, offset, data_flag, name):
        value_len = struct.unpack_from("=4xH", pgthb, offset)[0]
        layout = "=4xH%ds" % value_len
        names = ('%s len' % name, name)
        result = self.extract_data_from_pgthx(pgthb, offset, data_flag, layout, names)
        result[name] = str.rstrip(codecs.decode(result[name], 'cp1047_oe')).split('\00')
        del result[name][-1] # get rid of the last ''
        return result

    def extract_data_from_pgthd(self, pgthb, offset, data_flag):
        return self.extract_data_from_pgthx_string(pgthb, offset, data_flag, 'contty')

    def extract_data_from_pgthe(self, pgthb, offset, data_flag):
        return self.extract_data_from_pgthx_string(pgthb, offset, data_flag, 'path')

    def extract_data_from_pgthf(self, pgthb, offset, data_flag):
        return self.extract_data_from_pgthx_string(pgthb, offset, data_flag, 'command')

    def extract_data_from_pgthg(self, pgthb, offset, data_flag):
        layout = "=4x5I32s3I"
        names = ('limit_and_offset', 'count',
                 'max vnode tokens', 'current vnode tokens',
                 'server flags', 'server name',
                 'current files', 'max files',
                 'server type')
        result = self.extract_data_from_pgthx(pgthb, offset, data_flag, layout, names)
        limit = result['limit_and_offset'] >> 24
        offset = result['limit_and_offset'] & 0xFFFFFF
        result['server name'] = str.rstrip(codecs.decode(result['server name'], 'cp1047_oe'), " \x00")
        file_info = []
        for i in range(result['count']):
            data, offset = self.extract_data_from_pgthh(pgthb, offset)
            file_info.append(data)
        result['files'] = tuple(file_info)
        return result
    
    def extract_data_from_pgthh(self, pgthb, offset):
        layout = "=2sBBII"
        names = ('id', 'type', 'open', 'inode', 'devno')
        result = self.extract_data_from_pgthx(pgthb, offset, None, layout, names)
        result['id'] = codecs.decode(result['id'], 'cp1047_oe')
        offset += 12
        if result['id'][1] != 'p':
            return (result, offset)
        else:
            is_incomplete, name_length = struct.unpack_from('=BxH', pgthb, offset)
            name = codecs.decode(struct.unpack_from('4x%ds' % name_length, pgthb, offset)[0], 'cp1047_oe')
            if is_incomplete:
                name += '...'
                result['name'] = name
            return (result, offset + 4 + name_length)

    def show_data(self, pgthb, offset, remain):
        while remain > 0:
            print("%04X %r" % (offset, ["%04X" % v for v in struct.unpack_from("8H", pgthb, offset)]))
            remain -= 8 * 2
            offset += 8 * 2

    def extract_data_from_pgthj(self, pgthb, offset, data_flag):
        layout = '=4xIIQ4sIII4xHHIQ8s20s5s3xQQ'
        names = ('limit_and_offsetj', 'limit_and_offsetk','thread id','syscall',
                 'tcb address', 'cpu time ms', 'wait time ms', 'semaphore number',
                 'semaphore value', 'latch wait pid', 'signal pending mask',
                 'login name', 'last five syscalls', 'status', 'cpu time us', 'wait time us')
        results = []
        while True:
            result = self.extract_data_from_pgthx(pgthb, offset, data_flag, layout, names)
            result['login name'] = str.rstrip(codecs.decode(result['login name'], 'cp1047_oe'), " \x00")
            result['syscall'] = str.rstrip(codecs.decode(result['syscall'], 'cp1047_oe'), " \x00")
            last_five_syscalls = codecs.decode(result['last five syscalls'], 'cp1047_oe')
            result['last five syscalls'] = tuple([str.rstrip(last_five_syscalls[pos:pos+4]) for pos in range(0, 20, 4)])
            result['status'] = str.rstrip(codecs.decode(result['status'], 'cp1047_oe'), " \x00")
            offsetj = result['limit_and_offsetj'] & 0xFFFFFF
            results.append(result)
            if not offsetj:
                break
            offset += 0x6C
        return tuple(results)

    
def ps(pid=0, asid=0, loginname=None,
       process=True, command=False,
       path=False, fileinfo=False, filepath=False, thread=False):
    options = []
    if process: options.append('PROCESS')
    if command: options.append('COMMAND')
    if path: options.append('PATH')
    if fileinfo: options.append('FILE')
    if filepath: options.append('FILEPATH')
    if process: options.append('THREAD')
    return get_thread_entity(options,
                             pid=pid, thid=0, asid=asid, loginname=loginname)
