from zos_python import zos_system_call, SYSTEM_CALL__CALL
from zos_python import cp1047_oe
import codecs

from ctypes import *

def dump_ctypes_object(obj):
    size = sizeof(obj)
    addr = addressof(obj)
    for offset32 in range(0, size, 32):
        print("%X %04X  " % (addr+offset32, offset32), end='')
        for offset4 in range(0, 32, 4):
            print("%08X " % c_uint.from_address(addr+offset32+offset4).value, end='')
        print('')
    print('', flush=True)

sep = '_'

structure_classes = {}

def stringify(value, keyword):
    if isinstance(value, dict):
        return '_'.join(value.values())
    else:
        return str(value)

def Class(base_name, bases, keywords):
    keyword_values = tuple([(keyword, stringify(value, keyword)) for keyword, value in keywords.items()
                            if keyword[0] != sep and \
                               keyword != 'from_name' and \
                               value and \
                               not (keyword == 'size' and value == 4)])
    key = (base_name, keyword_values)
    if key not in structure_classes:
        name = base_name + '_' + '_'.join([value for keyword, value in keyword_values])
        structure_classes[key] = type(name, bases, keywords)
    return structure_classes[key]

class integer_superclass: 
    def __getattribute__(self, name):
        if name == 'value':
            value = super().__getattribute__(name)
            if self.boolean:
                return True if value else False
            if self.to_name and value in self.to_name:
                return self.to_name[value]
            return value
        else:
            return super().__getattribute__(name)
    def __setattr__(self, name, value):
        if name == 'value':
            if self.boolean:
                value = 1 if value else 0
            if self.from_name:
                value = self.from_name[value]
        super().__setattr__(name, value)

def integer(**keywords): # size, value, values, boolean
    if 'boolean' not in keywords:
        keywords['boolean'] = False
    if 'size' not in keywords:
        keywords['size'] = 4
    if 'values' in keywords:
        values = keywords['values']
        del keywords['values']
        if isinstance(values, dict):
            first_key = next(iter(values.keys()))
            if isinstance(first_key, int):
                keywords['to_name'] = values
                keywords['from_name'] = {value: key for key, value in values.items()}
            else:
                keywords['to_name'] = {value: key for key, value in values.items()}
                keywords['from_name'] = values
    if 'to_name' not in keywords:
        keywords['to_name'] = None
    if 'from_name' not in keywords:
        keywords['from_name'] = None
    return Class('integer', ({1:c_byte, 2:c_short, 4:c_int, 8:c_longlong}[keywords['size']], integer_superclass,), keywords)

class len1_and_chars_superclass(Structure):
    def __getattribute__(self, name):
        if name == 'value':
            return codecs.decode(bytes(self.data[:self.length.value]), encoding)
        else:
            return super().__getattribute__(name)
    def __setattr__(self, name, value):
        if name == 'value':
            self.length.value = len(value)
            self.data[:len(value)] = codecs.encode(value, encoding)
        else:
            super().__setattr__(name, value)

    def reset_length(self):
        self.length.value = self.data._length_

def len1_and_chars(**keywords): # size
    keywords['_fields_'] = [("length", integer(size=1, initial_value=0)), ("data", c_ubyte * keywords['size'])]
    return Class('len1_and_chars', (len1_and_chars_superclass,), keywords)

class length_and_pointer_to_chars_superclass(Structure):
    def __getattribute__(self, name):
        if name == 'value':
            length = self.length.value
            array = self.data_ptr.contents
            if length == array._length_ and (array[0] == 0):
                return '\\x00...'
            else:
                data = bytes(array[:length])
                if self.binary:
                    return data
                else:
                    return codecs.decode(data, encoding)
        else:
            return super().__getattribute__(name)
    def __setattr__(self, name, value):
        if name == 'value':
            self.length.value = len(value)
            if self.binary:
                self.data_ptr.contents[:len(value)] = value
            else:
                self.data_ptr.contents[:len(value)] = codecs.encode(value, encoding)
        else:
            superclass.__setattr__(name, value)

    def reset_length(self):
        self.length.value = self.data_ptr.contents._length_

def length_and_pointer_to_chars(**keywords): # size
    if 'pack' in keywords:
        keywords['_pack_'] = keywords['pack']
    if 'binary' not in keywords:
        keywords['binary'] = False
    keywords['_fields_'] = [("length", integer(initial_value=keywords['size'])), ("data_ptr", POINTER(c_ubyte * keywords['size']))]
    return Class('length_and_pointer_to_chars', (length_and_pointer_to_chars_superclass,), keywords)

def aligned_bytes(**keywords): # size, alignment
    size = keywords['size']
    alignment = keywords['alignment']
    element_class = {1: c_uint8, 2: c_uint16, 4: c_uint32, 8: c_uint64}[alignment]
    element_size = (size + (alignment - 1)) // alignment
    return Class('aligned_bytes', (element_class * element_size,), keywords)

def collect_pointer_fields(base_class, parent_field_names, fields, pointer_fields):
    for fname, fclass in base_class._fields_:
        if hasattr(fclass, '_fields_'):
            collect_pointer_fields(fclass, parent_field_names+(fname,), fields, pointer_fields)
        if hasattr(fclass, '_length_'):
            pass
        elif hasattr(fclass, '_type_') and not isinstance(fclass._type_, str):
            if fname.endswith("_ptr"):
                ftype = fclass._type_
                names = parent_field_names + (fname[:-4],)
                name = sep.join(names)
                fields.append((name, ftype))
                pointer_fields.append((parent_field_names+(fname,), name))
                if hasattr(ftype, '_fields_'):
                    collect_pointer_fields(ftype, (name,), fields, pointer_fields)
            else:
                print("Warning: pointer type fields need to have names ending in _ptr: %r" % fname)

def class_with_dependencies(base_class, superclass, debug=False):
    fields = list(base_class._fields_)
    pointer_fields = list()
    collect_pointer_fields(base_class, (), fields, pointer_fields)
    if debug:
        print("class_with_dependencies")
        print("superclass=%s" % superclass.__name__)
        print("class of superclass=%s" % superclass.__class__.__name__)
        for field in fields:
            print(field)
    keywords = {'_fields_': fields, '_pointer_fields_': pointer_fields}
    return Class(base_class.__name__ + '_with_dependencies', (superclass,), keywords)

def initialize_fields_of_class_with_dependencies(obj, initial_values_dict):
    for fname, fclass in obj._fields_:
        if hasattr(fclass, '_length_'):
            continue
        if hasattr(fclass, '_type_') and not isinstance(fclass._type_, str):
            continue
        fobj = getattr(obj, fname)
        if hasattr(fobj, 'initial_value_keyword') and fobj.initial_value_keyword in initial_values_dict:
            fobj.value = initial_values_dict[fobj.initial_value_keyword]
        elif hasattr(fobj, 'initial_value'):
            fobj.value = fobj.initial_value
        elif hasattr(fobj, '_fields_'):
            initialize_fields_of_class_with_dependencies(fobj, initial_values_dict)

def get_object(obj, names):
    if len(names) == 0:
        return obj
    else:
        return get_object(getattr(obj, names[0]), names[1:])

def initialize_pointers_of_class_with_dependencies(obj):
    for pointer_name, pointed_to_name in obj._pointer_fields_:
        get_object(obj, pointer_name).contents = getattr(obj, pointed_to_name)

def initialize_class_with_dependencies(obj, initial_values_dict):
    initialize_pointers_of_class_with_dependencies(obj)
    initialize_fields_of_class_with_dependencies(obj, initial_values_dict)

def reset_lengths_of_output_fields(obj):
    if hasattr(obj, 'reset_length') and hasattr(obj, 'reset') and obj.reset:
        obj.reset_length()
    elif hasattr(obj, '_fields_'):
        for field_name, field_class in obj._fields_:
            reset_lengths_of_output_fields(getattr(obj, field_name))

def show_fields(obj, path=(), debug=False):
    for field_name, field_class in obj._fields_:
        field_value = getattr(obj, field_name)
        path_with_field = path+(field_name,)
        if debug:
            print("%03X " % (addressof(field_value) - addressof(obj)), end='')
        if hasattr(field_value, '_length_'):
            if debug:
                print("%r %s (len=%d)" % (path_with_field, 'array', field_value._length_))
            value = None
        elif hasattr(field_value, 'value'):
            value = field_value.value
        elif hasattr(field_value, '_fields_'):
            if debug:
                print("%r %s" % (path_with_field, 'structure'))
            show_fields(field_value, path_with_field, debug)
            value = None
        elif hasattr(field_value, 'contents'):
            if debug:
                print("%r %s" % (path_with_field, 'pointer'))
            value = None
        else:
            if debug:
                print("%r %r" % (path_with_field, field_class))
            value = None
        if value is None:
            pass
        elif isinstance(value, str):
            if hasattr(field_value, 'length'):
                if len(value) > 0 and value[0] == '\x00':
                    value = '\\x00...'
                print("%r %r (length=%d)" % (path_with_field, value, field_value.length.value))
            else:
                print("%r %r" % (path_with_field, value))
        else:
            print("%r %r" % (path_with_field, value))

def CallArgs(base_class, fname, superclass, debug=False):
    if debug:
        print("CallArgs")
        print("superclass=%s" % superclass.__name__)
        print("class of superclass=%s" % superclass.__class__.__name__)
    keywords = dict(_fields_ = [('fn_and_rc', integer(size=8, initial_value_keyword=fname)),
                                    ('r0', integer(size=8)),
                                    ('args_ptr', POINTER(base_class)),
                                    ('save_area_ptr', POINTER(c_longlong * 18)),
                                    ('code', integer(size=8, initial_value=SYSTEM_CALL__CALL))])
    return Class('CallArgs_' + base_class.__name__, (superclass,), keywords)

certificate_maximum_length = 4096
private_key_maximum_length = 2048
label_maximum_length = 32
dn_maximum_length = 512
record_id_maximum_length = 246
# attribute_length, Record_ID_length, label_length, or CERT_user_ID
private_key_types =  {1:'PKCS PK', 2:'ICSF KTL', 3:'PCICC KTL', 5:'DH PK', 6:'ECC PK', 
                          7:'ECC KTL PKDS', 9:'RSA KTL TKDS', 11:'ECC KTL TKDS', 12:'DSA KTL TKDS'}

racf_get_data_handle_fields = [ \
    ('db_token', integer()), # reserved
    ('number_of_predicates', integer(initial_value_keyword='number_of_predicates')), # input: 0 or 1
    ('attribute_id', integer(initial_value_keyword='predicate_type', values={'label':1, 'default':2, 'dn':3})), # input
    ('attribute', length_and_pointer_to_chars(size=32, initial_value_keyword='predicate_value', pack=4)), # input
    ]

class racf_get_data_handle(Structure):
    _fields_ = racf_get_data_handle_fields

racf_get_data_parmlist_fields = [ \
    ('handle_ptr', POINTER(racf_get_data_handle)),
    ('certificate_usage', integer(values={2:'certauth', 8:'personal', 0:'site'})), # output
    ('default', integer(boolean=True)), # output: non-zero: default is True, otherwise False
    ('certificate', length_and_pointer_to_chars(size=certificate_maximum_length, binary=True, reset=True)),
    ('private_key', length_and_pointer_to_chars(size=private_key_maximum_length, binary=True, reset=True)),
    ('private_key_type', integer(values=private_key_types, reset=True)),
    ('private_key_bitsize', integer()), # output
    ('label', length_and_pointer_to_chars(size=label_maximum_length, reset=True)),
    ('cert_userid', len1_and_chars(size=8, initial_value='        ', reset=True)),
    ('subjects_dn', length_and_pointer_to_chars(size=dn_maximum_length, binary=True, pack=4, reset=True)),
    ('record_id', length_and_pointer_to_chars(size=record_id_maximum_length, binary=True, reset=True)),
    ('certificate_status', integer(values={0x80000000:'trust', 0x40000000:'hightrust', 0x20000000:'notrust', 0:'any'})),
    ]

class racf_get_data_parmlist(Structure):
    _fields_ = racf_get_data_parmlist_fields

#cert_info_fields = [ \
#    ('cert_owner', len1_and_chars(size=what)),
#    ('cert_name', len1_and_chars(size=what)),
#    ]
#
#class cert_info(Structure):
#    _fields_ = cert_info_fields
#                        
#ring_info_fields = [ \
#    ('ring_owner', len1_and_chars(size=what),
#    ('ring_name', len1_and_chars(size=what)),
#    ('cert_count', integer()),
#    ('cert_info_array', cert_info * what),
#    ]
#         
#class ring_info(Structure):
#    _fields_ = ring_info_fields
#    
#class ring_info_block(Structure):
#    _fields_ = [('count', integer()), ('ring_info_array', ring_info * what)]

ring_results_max_size = 65536

racf_get_ring_info_parmlist_fields = [ \
    ('search_type', integer(initial_value_keyword='search_type', values={0:'one', 1:'all_after', 2:'one_userid_all_after', 3:'one_ringname_all_after'})),
    ('result_size', integer(initial_value=ring_results_max_size)),
    ('result_ptr', POINTER(c_uint8 * ring_results_max_size)),
    ]

class racf_get_ring_info_parmlist(Structure):
    _fields_ = racf_get_ring_info_parmlist_fields

racf_datalib_function_codes = {'DataGetFirst':1, 'DataGetNext':2, 'DataAbortQuery':3, 'GetRingInfo':13}

# R_datalib (IRRSDL00 or IRRSDL64) callable service
racf_datalib_fields = [ \
    ('num_parms_ptr', POINTER(integer(initial_value=14))),
    ('work_area_ptr', POINTER(aligned_bytes(size=1024, alignment=8))),
    ('saf_return_code_alet_ptr', POINTER(integer(initial_value=0))),
    ('saf_return_code_ptr', POINTER(integer())), # output
    ('racf_return_code_alet_ptr', POINTER(integer(initial_value=0))),
    ('racf_return_code_ptr', POINTER(integer())), # output
    ('racf_reason_code_alet_ptr', POINTER(integer(initial_value=0))),
    ('racf_reason_code_ptr', POINTER(integer())), # output
    ('function_code_ptr', POINTER(integer(size=1, values=racf_datalib_function_codes))), # input 
    ('attributes_ptr', POINTER(integer(initial_value=(1 << 31)))), # show all private key types
    ('racf_userid_ptr', POINTER(len1_and_chars(size=8, initial_value_keyword='racf_userid'))), # input
    ('ring_name_ptr', POINTER(len1_and_chars(size=237, initial_value_keyword='ring_name'))), # input
    ]

class racf_datalib(Structure):
    _fields_ = racf_datalib_fields

racf_get_data_fields = [ \
    ('dl', racf_datalib),
    ('parmlist_version_ptr', POINTER(integer(initial_value=1))), # input, use 1 to specify Cert_status on the DataGetFirst and DataGetNext
    ('parmlist_ptr', POINTER(racf_get_data_parmlist)), # input
    ]

class racf_get_data(Structure):
    _fields_ = racf_get_data_fields

racf_get_ring_info_fields = [ \
    ('dl', racf_datalib),
    ('parmlist_version_ptr', POINTER(integer(initial_value=0))), # input
    ('parmlist_ptr', POINTER(racf_get_ring_info_parmlist)), # input
    ]

class racf_get_ring_info(Structure):
    _fields_ = racf_get_ring_info_fields


class SafError(Exception):
    # https://www.ibm.com/support/knowledgecenter/SSLTBW_2.2.0/com.ibm.zos.v2r2.ichd100/ich2d100238.htm
    pass

from threading import local

import zos.load
loaded_functions = local()
def load(name):
    if not hasattr(loaded_functions, name):
        fn = zos.load.load(name)
        if fn & 1:
            fn &= ~1 # remove the amode=64 indicator
        setattr(loaded_functions, name, fn)
    return getattr(loaded_functions, name)

getdata_error_codes = {
    (0,0,0):"The service was successful.",
    (4,0,0):"RACF is not installed.",
    (8,8,4):"Parameter list error occurred.",
    (8,8,8):"Not RACF-authorized to use the requested service.",
    (8,8,12):"Internal error caused recovery to get control.",
    (8,8,16):"Unable to establish a recovery environment.",
    (8,8,20):"Requested Function_code not defined.",
    (8,8,24):"Parm_list_version number not supported.",
    (8,8,28):"Error in Ring_name length or RACF_userid length.",
    (8,8,32):"Length error in attribute_length, Record_ID_length, label_length, or CERT_user_ID.",
    (8,8,36):"dbToken error. The token may be zero, in use by another task, or may have been created by another task.",
    (8,8,40):"Internal error while validating dbToken.",
    (8,8,44):"No certificate found.",
    (8,8,48):"One or more of the following input length fields were too small: Certificate_length, Private_key_length, or Subjects_DN_length.",
    (8,8,52):"Internal error while obtaining record private key data.",
    (8,8,56):"Parameter error - Number_predicates, Attribute_ID or Cert_status",
    (8,8,80):"Internal error while obtaining the key ring or z/OS",
    (8,8,72):"Caller not in task mode.",
    (8,8,92):"Other internal error.",
    (8,8,96):"The linklib (steplib or joblib) concatenation contains a non-APF authorized library.",
    }

class racf_get_data_with_dependencies_superclass(Structure):
   
    def __init__(self, racf_userid=None, ring_name=None, predicate_type=None, predicate_value=None, debug=False):
        self.debug = debug
        self.rc = None
        self.fn = load('IRRSDL64')
        initial_value_dict = {'IRRSDL64': self.fn}
        if racf_userid:
            initial_value_dict['racf_userid'] = racf_userid
        if ring_name:
            initial_value_dict['ring_name'] = ring_name
        if predicate_value:
            initial_value_dict['number_of_predicates'] = 1
            initial_value_dict['predicate_type'] = predicate_type or 'label'
            initial_value_dict['predicate_value'] = predicate_value
        initialize_class_with_dependencies(self, initial_value_dict)

    def values(self):
        try:
            self.args_dl_function_code.value = 'DataGetFirst'
            while True:
                self.call()
                if self.args_dl_saf_return_code.value or self.args_dl_racf_return_code.value or self.args_dl_racf_reason_code.value:
                    # https://www.ibm.com/support/knowledgecenter/SSLTBW_2.2.0/com.ibm.zos.v2r2.ichd100/ich2d100238.htm
                    codes = (self.args_dl_saf_return_code.value,
                                 self.args_dl_racf_return_code.value,
                                 self.args_dl_racf_reason_code.value)
                    if self.debug:
                        dump_ctypes_object(self)
                    if codes[0] == 8 and codes[1] == 8 and codes[2] == 44:
                        break
                    elif codes[0] == 8 and codes[1] == 12:
                        reason = "ICSF error return code=%02X reason code=%04X" % (codes[2]>>16, codes[2]&0xFFFF)
                    else:
                        reason = getdata_error_codes[codes]
                    raise SafError("%d %d %d %s" % (codes + (reason,)))
                yield {'certificate_usage': self.args_parmlist.certificate_usage.value,
                       'default': self.args_parmlist.default.value,
                       'certificate': self.args_parmlist.certificate.value,
                       'private_key': self.args_parmlist.private_key.value,
                       'private_key_type': self.args_parmlist.private_key_type.value,
                       'private_key_bitsize': self.args_parmlist.private_key_bitsize.value,
                       'label': self.args_parmlist.label.value,
                       'cert_userid': self.args_parmlist.cert_userid.value,
                       'subjects_dn': self.args_parmlist.subjects_dn.value,
                       'record_id': self.args_parmlist.record_id.value}
                self.args_dl_function_code.value = 'DataGetNext'
        finally:
            self.args_dl_function_code.value = 'DataAbortQuery'
            self.call()

    def call(self):
        if self.debug:
            print(self.args_dl_function_code.value)
        reset_lengths_of_output_fields(self)
        zos_system_call(self)
        self.rc = self.fn_and_rc.value
        self.fn_and_rc.value = self.fn


racf_get_data_call_args = CallArgs(racf_get_data, 'IRRSDL64', Structure)
racf_get_data_with_dependencies = class_with_dependencies(racf_get_data_call_args, racf_get_data_with_dependencies_superclass)

# userid in uppercase, or the reserved user IDs ('irrcerta' or 'irrsitec' in lowercase) or their alternate forms (*AUTH* or *SITE* in uppercase), or *TOKEN*
# ring_name
# A virtual key ring is the collection of certificates assigned to a given user ID, including the RACF reserved user IDs for CERTAUTH ('irrcerta' or '*AUTH*') and SITE ('irrsitec' or '*SITE*').
# A virtual key ring can be specified by coding an asterisk ('*') for the Ring_name with the corresponding RACF_user_ID, such as user01/* or *SITE*/*.

import asn1, sys, dump_asn1

def test_keyring(racf_userid='*SITE*', ring_name='*',
                     predicate_type=None, predicate_value=None,
                     limit=3, debug=False):
    obj = racf_get_data_with_dependencies(racf_userid=racf_userid, ring_name=ring_name,
                                          predicate_type=predicate_type, predicate_value=predicate_value,
                                          debug=debug)
    if debug:
        show_fields(obj, debug=debug)
        print('')
    for (n, result) in enumerate(obj.values()):
        for key, value in result.items():
            if isinstance(value, bytes) and len(value)>0 and key != 'record_id':
                decoder = asn1.Decoder()
                decoder.start(value)
                print("%s:" % (key,))
                dump_asn1.pretty_print(decoder, sys.stdout)
            else:
                print("%s: %r" % (key, value))
        print('')
        if n >= limit:
            break

if __name__ == "__main__":
    # , predicate_type='label', predicate_value='mylabel'
    test_keyring(racf_userid='*SITE*', ring_name='*', limit=3)

