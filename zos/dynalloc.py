from zos._bytearray import *
from zos._system_call import *

import codecs
cp1047_oe = 'cp1047_oe'
try:
    codecs.lookup(cp1047_oe)
except LookupError:
    cp1047_oe = 'cp1047'

import collections
import struct

from .dynalloc_definitions import *

def process_text_units(text_unit_mapping, keyword_definitions, text_unit_array, tu_input=True, verbose=False):
    if text_unit_array:
        text_unit_array_address = bytearray_buffer_address(text_unit_array)
    return_mapping = {} if not tu_input else None
    tu_count = len(text_unit_mapping.items())
    ptr_offset = 0
    size = tu_count * 4
    count = 0
    for key, value in text_unit_mapping.items():
        count += 1;
        definition = keyword_definitions[key]
        if verbose:
            print(definition)
        tu_type = definition[KEYWORD_DEFINITION_TYPE]
        max_len = definition[KEYWORD_DEFINITION_MAX_LEN]
        max_value_count = definition[KEYWORD_DEFINITION_MAX_COUNT]
        code = definition[KEYWORD_DEFINITION_KEY]
        return_value = definition[KEYWORD_DEFINITION_RETURN] if len(definition) >= (KEYWORD_DEFINITION_RETURN+1) else None
        if not tu_input and not return_value:
            continue
        if text_unit_array:
            tu_offset = (count - 1) * 4
            if tu_input:
                struct.pack_into("I", text_unit_array, tu_offset, text_unit_array_address + size + (0 if count < tu_count else 1<<31))
                struct.pack_into("H", text_unit_array, size, code)
            else:
                size = (struct.unpack_from("I", text_unit_array, tu_offset)[0] & 0x7FFFFFFF) - text_unit_array_address
        size += 2
        if (code == DALSYSOU and value == '*') or (code == DALSSNM and value is None) or max_value_count == 0:
            value = ()
            min_value_count = 0
        else:
            min_value_count = 1
        if tu_input:
            if return_value:
                value_count = max_value_count
            else:
                if isinstance(value, str) or not isinstance(value, collections.Iterable):
                    value = (value,)
                value_count = len(value)
                if value_count > max_value_count or value_count < min_value_count:
                    raise ValueError
            if text_unit_array:
                struct.pack_into("H", text_unit_array, size, value_count)
        else:
            value = []
            value_count = struct.unpack_from("H", text_unit_array, size)[0]
        size += 2
        for element in value if not return_value else range(value_count):
            if return_value:
                if tu_input:
                    if text_unit_array:
                        struct.pack_into("H", text_unit_array, size, max_len)
                    size += 2 + max_len
                else:
                    len_element = struct.unpack_from("H", text_unit_array, size)[0]
                    size += 2
                    if tu_type == KD_TYPE_VARCHAR:
                        element = str.rstrip(codecs.decode(struct.unpack_from("%ds" % len_element, text_unit_array, size)[0],
                                                           cp1047_oe))
                    else:
                        offset = 0
                        if len_element == 1:
                            fmt = 'B'
                        elif len_element == 2:
                            fmt = 'H'
                        elif len_element == 3:
                            fmt = 'I'
                        else:
                            fmt = 'I'
                        element = struct.unpack_from(fmt, text_unit_array, size + offset)[0]
                        if len_element == 3:
                            element = element & 0xFFFFFF
                        if isinstance(tu_type, collections.Mapping):
                            pass # FIXME. invert the mapping and use it to decode the value
                    value.append(element)
                continue
            if isinstance(element, str):
                if isinstance(tu_type, collections.Mapping):
                    element = tu_type[element]
                else:
                    element = codecs.encode(element, encoding=cp1047_oe)
            if isinstance(element, int):
                if text_unit_array and tu_input:
                    struct.pack_into("H", text_unit_array, size, max_len)
                size += 2
                nb = max_len
                while nb > 0:
                    if text_unit_array and tu_input:
                        text_unit_array[size + nb - 1] = element & 0xFF
                    element = element >> 8
                    nb -= 1
                size += max_len
                continue
            len_element = len(element)
            if text_unit_array and tu_input:
                struct.pack_into("H", text_unit_array, size, len_element)
            size += 2
            if text_unit_array and tu_input:
                struct.pack_into("%ds" % len_element, text_unit_array, size, element)
            size += len_element
        if not tu_input:
            if max_value_count == 1:
                value = value[0]
            return_mapping[definition[KEYWORD_DEFINITION_NAMES][0]] = value
    return size if tu_input else return_mapping

def print_message(message):
    print(message)

MAX_EM_MESSAGES = 8

IEFDB476 = None

def get_IEFDB476():
    global IEFDB476
    if IEFDB476:
        return IEFDB476
    from zos.load import load
    IEFDB476 = load('IEFDB476')
    return IEFDB476
    
import os

def retrieve_dynalloc_messages(message_function, verbName, keyword_definitions, svc99rbx, svc99rb, svc_args,
                               verbose=False):
    svc99_rc = struct.unpack_from('L', svc_args, 0)[0]
    s99error = struct.unpack_from('H', svc99rb, 4)[0]
    s99info = struct.unpack_from('H', svc99rb, 6)[0]
    if svc99_rc != 0:
        message_function("%s failed, return code=%d, error=%04X, info=%04X" % (verbName, svc99_rc, s99error, s99info))
    block_count = svc99rbx[11]
    if verbose:
        print("s99rbx message_count = %d" % block_count)
    if block_count == 0:
        return
    if block_count > MAX_EM_MESSAGES:
        block_count = MAX_EM_MESSAGES

    emMessages = bytearray_set_address_size(bytearray(256 * block_count), 31)
    
    emCall = bytearray_set_address_size(bytearray(28), 31)
    struct.pack_into('BBBxII4xI', emCall, 0,
                         0x20, 50, block_count,
                         bytearray_buffer_address(svc99rb), svc99_rc, bytearray_buffer_address(emMessages))
    if verbose:
        print(["%08X" % v for v in struct.unpack_from('IIIII', emCall, 0)])

    emCallPlist = bytearray_set_address_size(bytearray(4), 31)
    struct.pack_into('I', emCallPlist, 0, 0x80000000 | bytearray_buffer_address(emCall))
                         
    save_area = bytearray_set_address_size(bytearray(18*4), 31)

    call_args = bytearray(5*8)
    struct.pack_into('QQQQQ', call_args, 0,
                     get_IEFDB476(), 0, bytearray_buffer_address(emCallPlist), bytearray_buffer_address(save_area), SYSTEM_CALL__CALL31)

    zos_system_call(call_args)
    IEFDB476_rc = struct.unpack_from('Q', call_args, 0)[0]
    if verbose:
        print("IEFDB476_rc=%X" % IEFDB476_rc)

    if verbose:
        print(["%X" % v for v in struct.unpack_from('xxBBIIHHI', svc99rbx, 16)])
        print(["%X" % v for v in struct.unpack_from('BBBxII4xI', emCall, 0)])
        print("block_count=%X" % block_count)
    for i in range(block_count):
        message_length = struct.unpack_from('H', emMessages, 256*i)[0]
        if verbose:
            print('message_length=%d' % message_length)
        message_text = emMessages[256*i+4 : 256*i+4+ message_length]
        message = str.rstrip(codecs.decode(message_text, cp1047_oe))
        message_function(message)

    if s99error == 0x035C: # Invalid PARM specified in text unit, with corresponding message IKJ56231I
        info = keyword_definitions[s99info]
        if info:
            message_function("text unit %04X is %s %s" % (s99info, info[0][0], info[0][2]))

def dynallocInternal(verb, text_unit_mapping, flags1=0, flags2=0,
                     verbose=False, message_level=0, message_function=print_message):
    keyword_definitions = text_keyword_definitions[verb]
    text_unit_array_size = process_text_units(text_unit_mapping, keyword_definitions, None, verbose=verbose)
    if verbose:
        print("test_unit_array_size = %r" % text_unit_array_size)
    text_unit_array = bytearray_set_address_size(bytearray(text_unit_array_size), 31)
    process_text_units(text_unit_mapping, keyword_definitions, text_unit_array, verbose=verbose)
    if verbose:
        show_text_units(text_unit_array)

    message_severity_level = 0 # informational, that is, include all the messages 
    message_block_subpool = 4
    message_options = 0x48 # return message to caller + specified subpool
    
    svc99rbx = bytearray_set_address_size(bytearray(36), 31)
    struct.pack_into('BBBBBBBBBBB', svc99rbx, 0,
                         0xE2, 0xF9, 0xF9, 0xD9, 0xC2, 0xE7, 1, #'S99RBX', version
                         message_options, message_block_subpool, 8, message_severity_level)

    svc99rb = bytearray_set_address_size(bytearray(20), 31)
    struct.pack_into('BBHHHIII', svc99rb, 0,
                     20, verb_codes[verb], flags1, 0, 0, bytearray_buffer_address(text_unit_array), bytearray_buffer_address(svc99rbx), flags2)

    svc99plist = bytearray_set_address_size(bytearray(4), 31)
    struct.pack_into('I', svc99plist, 0,
                     0x80000000 | bytearray_buffer_address(svc99rb))

    svc_args = bytearray(5*8)
    struct.pack_into('QQQQQ', svc_args, 0,
                     0, 0, bytearray_buffer_address(svc99plist), 99, SYSTEM_CALL__SVC)

    zos_system_call(svc_args)
    svc99_rc = struct.unpack_from('L', svc_args, 0)[0]
    
    if verbose:
        s99error_and_info = struct.unpack_from('HH', svc99rb, 4)
        print("s99rc=%X, error=%04X, info=%04X" % (svc99_rc, s99error_and_info[0], s99error_and_info[1]))
        show_text_units(text_unit_array)
    retrieve_dynalloc_messages(message_function, verb, keyword_definitions, svc99rbx, svc99rb, svc_args,
                               verbose=verbose)
    
    output_mapping = process_text_units(text_unit_mapping, keyword_definitions, text_unit_array, tu_input=False, verbose=verbose)
    return (svc99_rc, output_mapping)

verb_codes = {'allocate':0x01,
              'unallocate':0x02,
              'concatenate':0x03,
              'deconcatenate':0x04,
              'remove_in_use_attribute':0x05,
              'ddname_allocate':0x06,
              'information_retrieval':0x07}

def dynalloc(text_unit_mapping, flags1=0, flags2=0,
             verbose=False, message_level=0, message_function=print_message):
    return dynallocInternal('allocate', text_unit_mapping, flags1=flags1, flags2=flags2, 
                            verbose=verbose, message_level=message_level, message_function=message_function)

def dynunalloc(text_unit_mapping, flags1=0, flags2=0,
               verbose=False, message_level=0, message_function=print_message):
    return dynallocInternal('unallocate', text_unit_mapping, flags1=flags1, flags2=flags2, 
                            verbose=verbose,  message_level=message_level, message_function=message_function)

def dynconcatenate(text_unit_mapping, flags1=0, flags2=0,
                   verbose=False, message_level=0, message_function=print_message):
    return dynallocInternal('concatenate', text_unit_mapping, flags1=flags1, flags2=flags2, 
                            verbose=verbose, message_level=message_level, message_function=message_function)

def dyninformation(text_unit_mapping, flags1=0, flags2=0,
                   verbose=False, message_level=0, message_function=print_message):
    return dynallocInternal('information_retrieval', text_unit_mapping, flags1=flags1, flags2=flags2, 
                            verbose=verbose, message_level=message_level, message_function=message_function)

def show_text_units(text_unit_array):
    text_unit_array_address = bytearray_buffer_address(text_unit_array)
    end = False
    tu_count = 0
    while not end:
        tu_address = struct.unpack_from("I", text_unit_array, tu_count * 4)[0]
        offset = tu_address - text_unit_array_address
        tu_count += 1
        end = 0 != (offset & 0x80000000)
        offset = offset & 0x7FFFFFFF
        code = struct.unpack_from("H", text_unit_array, offset)[0]
        offset += 2
        count = struct.unpack_from("H", text_unit_array, offset)[0]
        offset += 2
        print("%04X %04X " % (code, count), end=('\n' if count == 0 else ''))
        for index in range(count):
            if index > 0:
                print("          ", end='')
            length = struct.unpack_from("H", text_unit_array, offset)[0]
            offset += 2
            print("%04X " % length, end='')
            data = struct.unpack_from("%ds" % length, text_unit_array, offset)[0]
            offset += length
            for i in range(len(data)):
                print("%02X" % data[i], end=' ')
            print('')
    

        
