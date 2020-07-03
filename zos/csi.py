
import codecs
import struct
import sys

IGGCSI00 = None

def get_IGGCSI00():
    global IGGCSI00
    if IGGCSI00:
        return IGGCSI00
    from zos.load import load
    IGGCSI00 = load('IGGCSI00')
    return IGGCSI00

max_csi_fields = 50
csi_results_total_size = 64*1024

class catalog_info:
    csi_parameters = bytearray(3*44+16+5*1+2+max_csi_fields*8).set_address_size(31)
    csi_results = bytearray(csi_results_total_size).set_address_size(31)
    csi_reason_code = bytearray(4).set_address_size(31)
    struct.pack_into('=I', csi_results, 0,
                         csi_results_total_size)
    arglist = bytearray(3*4).set_address_size(31)
    struct.pack_into('=III', arglist, 0, 
                         csi_reason_code.buffer_address(), csi_parameters.buffer_address(), csi_results.buffer_address())
    save_area = bytearray(18*4).set_address_size(31)
    call31 = bytearray(5*8)

    def get_catalog_info(self, dsname, requested_fields=None, types=""):
        ctypes.memset(csi_parameters.buffer_address(), 0x40, len(csi_parameters)) # 0x40 is ' ' in ebcdic
        if requested_fields == "extents":
            requested_fields = ("ENTYPE", "VOLSER", "NOEXTNT")
        elif requested_fields == "alias":
            requested_fields = ("ENTYPE", "TYPE", "NAME")
        elif requested_fields == "nonvsam":
            requested_fields = ("NVSMATTR",)
            types = "ABH"
        elif not requested_fields:
            requested_fields = [v[0] for v in csi_fields.keys()]
        if len(requested_fields) >= max_csi_fields:
            raise Exception("%d fields requested, but %d fields is the limit" % (len(requested_fields), max_csi_fields))
        struct.pack_into('=44s', self.csi_parameters, 0,
                    codecs.encode("{:44s}".format(dsname), encoding='cp1047_oe'))
        struct.pack_into('=1s', self.csi_parameters, 3*44+16, # use_fullword_offsets
                    codecs.encode("{:1s}".format('Y'), encoding='cp1047_oe'))
        struct.pack_into('=1s', self.csi_parameters, 3*44+16+4*1, # match_on_cluster_name
                    codecs.encode("{:1s}".format('F'), encoding='cp1047_oe'))
        struct.pack_into('=H', self.csi_parameters, (3*44+16+5*1),
                             len(requested_fields))
        for field_number, field_name in enumerate(requested_fields):
            struct.pack_into('=8s', self.csi_parameters, (3*44+16+5*1+2+field_number*8),
                            codecs.encode("{:8s}".format(field_name), encoding='cp1047_oe'))
        while True:
            struct.pack_into('QQQQQ', self.call31, 0,
                            get_IGGCSI00(), 0, self.arglist.buffer_address(),
                            self.save_area.buffer_address(), os.SYSTEM_CALL__CALL31)
            csi_return_code = struct.unpack_from('=4xI', self.call31, 0)[0] 
            if csi_return_code != 0:
                module_id, return_code, reason_code = struct.unpack_from('=2sBB', self.csi_reason_code, 0)
                module_id = codecs.decode(module_id, 'cp1047_oe')
                if return_code == 0x64:
                    if csi_return_code == 4 and reason_code == 0x04:
                        # dataset: locate the entry or entries with the CSIENTER flag set and inspect the CSIRETN field for further info
                        pass
                    elif csi_return_code == 4 and reason_code == 0x08:
                        # catalog: inspect the return code and reason code for the catalog entry for further information.
                        pass
                    elif csi_return_code == 8 and reason_code == 0x08:
                        # what?
                        pass
                else:
                    raise Exception("CSI failed rc=%X, reason=%X, return=%X, module=%.2s" % \
                                        (csi_return_code, reason_code, return_code, module_id))
                break
            total_size, required_length, used_length, number_of_fields = struct.unpack_from("=IIIH", self.csi_results, 0)
            offset = 14
            while offset < used_length:
                entry_flag, entry_type, entry_name = struct.unpack_from("=B1s44s", self.csi_results, offset)
                offset += 46
                entry_type = codecs.decode(entry_type, 'cp1047_oe')
                entry_name = codecs.decode(entry_name, 'cp1047_oe').rstrip()
                entry = {'name':entry_name, 'type':entry_type}
                if entry_type == '0' or (entry_flag & 0x40): # CSI_ENTRY_HAS_ERROR
                    module_id, return_code, reason_code = struct.unpack_from('=2sBB', self.csi_results, offset)
                    offset += 4
                    module_id = codecs.decode(module_id, 'cp1047_oe')
                    entry['error_module_id'] = module_id
                    entry['return_code'] = return_code
                    entry['reason_code'] = reason_code
                if entry_type != '0' and (entry_flag & 0x20): # CSI_ENTRY_HAS_DATA
                    entry_data_size = struct.unpack_from('=I', self.csi_results, offset)
                    offset += 4
                    number_of_data_fields = number_of_fields + 1
                    field_length_offset = offset;
                    for field_index in range(number_of_data_fields):
                        field_name = requested_fields[field_index]
                        field_description = csi_field_descriptions[field_name]
                        field_length = struct.unpack_from('=i', self.csi_results, field_length_offset + field_index * 4)[0]
                        fdescr_length = field_description['length']
                        fdescr_type = field_description['type']
                        if field_length == -1:
                            continue # suppressed because of a security issue
                        if fdescr_length == 0:
                            field_length = struct.unpack_from('=H', self.csi_results, offset)
                            offset += 2
                            entry['data'] = codecs.decode(struct.unpack_from('=%ds' % field_length, self.csi_results, offset), 'cp1047_oe').rstrip()
                            offset += field_length
                        else:
                            multiplicity = field_length / fdescr_length;
                            values = []
                            for number in range(multiplicity):
                                if fdescr_type == 'char':
                                    value = codecs.decode(struct.unpack_from('=%ds' % fdescr_length, self.csi_results, offset), 'cp1047_oe').rstrip()
                                elif fdescr_type == 'int':
                                    value = int.from_bytes(struct.unpack_from('=%ds' % fdescr_length, self.csi_results, offset), sys.byteorder)
                                elif fdescr_type == 'bit':
                                    bits = struct.unpack_from['=B', self.csi_results, offseta]
                                    value = []
                                    for bit_number, bit_name in enumerate(field_description['names']):
                                        if bits & (1<<(7-bit_number)):
                                            value.append(bit_name)
                                elif fdescr_type == 'enum':
                                    value = field_description['names'][struct.unpack_from['=B', self.csi_results, offseta]]
                                else:
                                    value = None
                                if value:
                                    values.append(value)
                                offset += fdescr_length
                            entry['data'] = tuple(values)
                    yield entry

if __name__ == '__main__':
    dsname = argv[1]
    requested_fields=None
    types=""
    csi = catalog_info()
    csi.get_catalog_info(dsname=dsname, requested_fields=requested_fields, types=types):

"""
struct csi_field_description {
  char *name;
  unsigned char length;
  unsigned char type;
#define FIELD_TYPE_CHAR 1
#define FIELD_TYPE_INT  2
#define FIELD_TYPE_BIT  3
#define FIELD_TYPE_ENUM 4
  struct value_name_list {
    unsigned char value;
    char *name;
  } value_name_array[20];
} csi_field_descriptions[] = {
  {"DEVTYP",   4, FIELD_TYPE_INT,  {{0, 0}}}, /* ucb device type */
  {"ENTYPE",   1, FIELD_TYPE_ENUM, /* entry type */
   {{'A', "Non-VSAM data set"},
    {'B', "Generation data group"},
    {'C', "Cluster"},
    {'D', "Data component"},
    {'G', "Alternate index"},
    {'H', "Generation data set"},
    {'I', "Index component"},
    {'L', "ATL Library entry"},
    {'R', "Path"},
    {'U', "User catalog connector entry"},
    {'W', "ATL Volume entry"},
    {'X', "Alias"},
    {0, 0}}},
  {"TYPE",     1, FIELD_TYPE_CHAR, {{'A', "non-vsam"},{'B', "GDG"},{'H', "GDS"},{0, 0}}},
  {"NAME",     44, FIELD_TYPE_CHAR,{{0, 0}}},
  {"FILESEQ",  2, FIELD_TYPE_INT,  {{0, 0}}},
  {"GENLEVEL", 4, FIELD_TYPE_CHAR, {{0, 0}}}, /* GDG generation level dddd */
  {"NVSMATTR", 1, FIELD_TYPE_ENUM, {{'H', "ActiveGDS"},{'N', "DeferredGDS"},{'M', "RolledOffGDS"},{0x00, "simple"},{'L', "ExtendedPartitionedDataSet"}, {'P', "Posix"}, {0,0}}},
  {"COMPIND",  1, FIELD_TYPE_BIT,  {{0x40, "extended"}, {0x20, "compressible"}, {0, 0}}},
  {"STRIPCNT", 2, FIELD_TYPE_INT,  {{0, 0}}}, /* stripe count */
  {"COMUDSIZ", 8, FIELD_TYPE_INT,  {{0, 0}}}, /* user data size after compression */
  {"UDATASIZ", 8, FIELD_TYPE_INT,  {{0, 0}}}, /* user data size (not includeing BDWs for VB) */
  {"VOLSER",   6, FIELD_TYPE_CHAR, {{0, 0}}}, /* all asterisks=ipl volume, may contaain symbolic parameters */
  {"VVRNFLGS", 2, FIELD_TYPE_BIT,  {{0x80, "invalid UDATASIZ"},{0x7F, "block level compression"}}},
  {"VOLFLG",   1, FIELD_TYPE_BIT,  {{0x80, "primary volume with space"},{0x40, "candidate volume with no space"},{0, 0}}},
  {"DSCBTTR",  3, FIELD_TYPE_INT,  {{0, 0}}}, /* TTR of format 1 DSCB */
  {"DSCRDT2",  4, FIELD_TYPE_INT,  {{0, 0}}}, /* packed creation date YYDDDFCC */
  {"DSEXDT2",  4, FIELD_TYPE_INT,  {{0, 0}}}, /* packed expiration date YYDDDFCC */
  {"GDGALTDT", 4, FIELD_TYPE_INT,  {{0, 0}}}, /* packed alteration date YYDDDFCC */
  {"DATACLAS", 0, FIELD_TYPE_CHAR, {{0, 0}}},
  {"MGMTCLAS", 0, FIELD_TYPE_CHAR, {{0, 0}}},
  {"STORCLAS", 0, FIELD_TYPE_CHAR, {{0, 0}}},

  {"XHARBA",   8, FIELD_TYPE_INT,  {{0, 0}}}, 
  {"XHARBADS", 8, FIELD_TYPE_INT,  {{0, 0}}}, 
  {"XHURBA",   8, FIELD_TYPE_INT,  {{0, 0}}}, 
  {"XHURBADS", 8, FIELD_TYPE_INT,  {{0, 0}}}, 

  {"NOEXTNT",  1, FIELD_TYPE_INT,  {{0, 0}}},

  {"PRIMSPAC", 3, FIELD_TYPE_INT,  {{0, 0}}},
  {"SCONSPAC", 3, FIELD_TYPE_INT,  {{0, 0}}},
  {"",0,0,{{0,0}}}
};

typedef struct csi_field_description CSI_FIELD_DESCRIPTION;

#define MAX_REQUEST_FIELDS 50

struct csi_parameters {
  char generic_filter[44];
  char catalog_name[44];
  char resume_name[44];
  char types[16];  /* fill with blanks to get all types except tape */
  char match_on_cluster_name; /* Y or blanks */
  char resume;                /* Y or blank, set by CSI on return */
  char use_one_catalog;       /* Y or blank */
  char use_fullword_offsets;   /* F or blank */
  unsigned short number_of_fields;
  char fields[MAX_REQUEST_FIELDS][8];
};

typedef struct csi_parameters CSI_PARAMETERS;

struct csi_results {
  int total_size;
  int required_length; /* if insufficient for 1 cat entry and 1 entry */
  int used_length;
  short number_of_fields;  /* 1 greater than number of fields */
};

typedef struct csi_results CSI_RESULTS;

struct csi_error {
  char module_id[2];
  unsigned char reason_code;
  unsigned char return_code;
};

typedef struct csi_error CSI_ERROR;

#if CSI_TWO_BYTE_LENGTHS
typedef unsigned short CSI_LENGTH;
#else
typedef unsigned int CSI_LENGTH;
#endif

struct csi_entry_data {
  CSI_LENGTH length;
  CSI_LENGTH reserved;
  CSI_LENGTH field_lengths[1];  /* reference higher indices ok */
};

typedef struct csi_entry_data CSI_ENTRY_DATA;

struct csi_entry {
  unsigned char flag;
  char type;  /* 0;A,B,C,D,G,H,I,R,X,U,L,W */
  char name[44];
};

typedef struct csi_entry CSI_ENTRY;

#define CSI_CATALOG_NOT_SUPPORTED 0x80
#define CSI_CATALOG_NO_ENTRY_FOUND 0x40
#define CSI_CATALOG_DATA_INCOMPLETE 0x20
#define CSI_CATALOG_UNPROCESSED   0x10
#define CSI_CATALOG_PARTIALLY_PROCESSED 0x08

#define CSI_ENTRY_IS_PRIMARY  0x80
#define CSI_ENTRY_HAS_ERROR   0x40
#define CSI_ENTRY_HAS_DATA    0x20

#pragma pack(reset)
"""
