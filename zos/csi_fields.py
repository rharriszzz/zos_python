
('CanRepeat','Type',Length,'Name','Description')

('no','Character', 36,'ACTOKEN','Active compression dictionary token'),
('no','Fixed', 2,'AKEYPOS','The relative position in the data record of this AIX key.'),
# Only applicable for catalog entry types of AIX. Note that the field is only valid if the component type is "D" and the record type is for a alternate index.
('no','Fixed', 8,'AMDCIREC','Control interval size for 4 bytes and maximum record size for 4 bytes'),
('no','Fixed', 4,'AMDKEY','Relative position of KSDS key for 2 bytes and key length of KSDS key for 2 bytes'),
('yes','Character', 45,'ASSOC','A repeating list of catalog records associated with this entry. Consists of a 1-byte value similar to field name ENTYPE, followed by the 44-byte name of the association.'),
('no',{'symbolic':0x80, 'not symbolic':0x00}, 1,'ASSOCSYB Indicates whether the entry is a symbolic.'),
('yes','Character', 45,'ASSOCSYM','A repeating list of catalog records associated with this entry. Consists of a 1-byte value similar to field name ENTYPE, followed by the 44-byte name of the association.'),
('no',{'Speed':0x80, 'Unique':0x40, 'Reusable':0x20, 'Erase':0x10, 'ECSHARING':0x08,'Inhibit update':0x04,'Temporary export':0x20,'Track overflow':0x01}, 'Bitstring', 1,'ATTR1 Attributes:'),
('no',{'Region=1':(0xC0,0x00), 'Region=2':(0xC0,0x40), 'Region=3':(0xC0,0x80), 'Region=4':(0xC0,0xC0), 'System=1':(0x30,0x00), 'System=2':(0x30,0x10), 'System=3':(0x30,0x20), 'System=4':(0x30,0x30)}, 1,'ATTR2','Share attributes'),
('no','Fixed', 2,'BUFND','The number of buffers requested for Data'),
('no','Fixed', 2,'BUFNI','The number of buffers requested for Index'),
('no','Fixed', 4,'BUFSIZE','Maximum buffer size'),
('no','Fixed', 2,'CATACT','Catalog Activity count (Z entry type only)'),
('no',{'Open':0x8000, 'Master':0x4000, 'active in In-Storage Cache':0x2000, 'active in VLF':0x1000, 'ECS-active':0x0800, 'open in RLS mode':0x0400, 'deleted':0x0200, 'locked':0x0100}, 'Bitstring', 2,'CATFLAGS','(Z entry type only)'),
('no',{'swap':0x02, 'pagespace':0x01}, 1, 'CATTR','Attributes for pagespace and swapspace'),
('no', 'Addr', 4, 'CATUCB','UCB pointer for volume the catalog is on (Z entry type only'),
('no',{'extended format':0x40, 'compressible':0x20}, 1,'COMPIND','Compression indicator'),
('no','Fixed', 8,'COMUDSIZ','Compressed user data size'),
('no','Character','VL','DATACLAS','SMS data class'),
('yes','Fixed', 4,'DEVTYP','UCB device type'),
('yes','Fixed', 3,'DSCBTTR','TTR of format-1 DSCB for non-VSAM data set'),
('no','Mixed', 4,'DSCRDT2','Creation date. Packed decimal YYDDDF for 3 bytes appended with one byte century indicator. If the century byte is 00 then add 1900 to get the year; if 01, add 2000.'),
('no','Mixed', 4,'DSEXDT2','Expiration date. Packed decimal YYDDDF for 3 bytes appended with one byte century indicator. If the century byte is 00 then add 1900 to get the year; if 01, add 2000.'),
('no',{'not specified':0x00, 'NO':0x01, 'OPT':0x02, 'unused, not specified':0x03}, 1,'EATTR','Data set attribute for controlling allocation of VSAM data sets (note that EATTR for Non-VSAM data sets is not carried in the catalog information for such data sets).'),
('no',{'Not encrypted':0x00, 'Encrypted':0x01}, 1,'ENCRYPTF','the encryption flag.'),
('no','Fixed', 2,'ENCRYPTT','A 2 byte integer for the encryption type. '),
#It is initialized to x'0100'. If the data set is not encrypted, hex 'FFFF' is returned. Encryption type is intended for possible future types of encryption.
('no',(('Fixed',2,'encryption type'),('Fixed',64,'Key label'),('Fixed',8,'first half of saved ICV'),('Fixed',1,'mode'),('Fixed',16,'verification value'),('Fixed',5,'Reserved')), 96,'ENCRYPTA','All of the encryption fields as one field.'),
('no','Character', 44,'ENTNAME','The name of the entry'),
('no','Character', 1,'ENTYPE','Entry type, ex., 'C' is cluster, 'A' is non-VSAM, etc.'),
('no','Character', 8,'EXCPEXIT','Exception exit'),
('yes','Fixed', 2,'FILESEQ','File sequence number'),
('no',{'not zfs':0x00, 'zfs':'0x80','N/A':0xFF}, 1,'FSDSFLAG','File System Data Set Flag'),
('no','Mixed', 4,'GDGALTDT','Last alteration date. Packed decimal YYDDDF for 3 bytes appended with one byte century indicator. If the century byte is 00 then add 1900 to get the year; if 01, add 2000.'),
('no',{'Delete ALL GDSs when GATLIMIT exceeded':0x80, 'Scratch dataset when rolled off':0x40, 'Allocate GDSs in FIFO order':0x20, 'GDS PURGE':0x10, 'GDG Extended':0x08}, 1,'GDGATTR','Generation data group attributes'),
('no','Fixed', 1,'GDGLIMIT','Maximum number of generation data sets allowed in the GDG'),
('no','Fixed', 2,'GDGLIMTE','Maximum number of generation data sets allowed in the GDG or GDG extended (GDGE)'),
# Note: The use of the GDGLIMIT field name will be tracked by z/OS Generic Tracker when GDGLIMITE is not also
#present. The usage can be displayed with the DISPLAY GTZ,TRACKDATA console command when GDZTRACK is
# active. IBM recommends only using GDGLIMTE.
('yes','Character', 4,'GENLEVEL','GDG generation level for each active generation in EBCDIC format '),
('yes','Fixed', 4,'HARBA','High-allocated RBA'),
('no','Fixed', 4,'HARBADS','Data set high-allocated RBA'),
('yes','Character', 'VL','HIKEYV','High Key on volume'),
('no','Fixed', 4,'HILVLRBA','RBA of High Level Index Record'),
('yes','Fixed', 4,'HKRBA','RBA of data control interval with high key'),
('yes','Fixed', 4,'HURBA','High-used RBA for the volume requested'),
('no','Fixed', 4,'HURBADS','Data set high-used RBA'),
('no','Fixed', 2,'INDXLVLS','Number of Index Levels'),
('yes',{'Sequence set with data':0x80, 'Extents not preformatted':0x40, 'Converted VSAM data set volume':0x20}, 1,'ITYPEXT','Type of extent'),
('no','Character', 64,'KEYLABEL','The field name for key label and the data returned is 64 characters in length. If the data set is not encrypted, 64 bytes of hex 'FF's are returned.'),
('no','Character', 16,'LOCKSTNM','Data Set Lock Structure Name (RLS eligible data sets only)'),
('no',{'LOG(NONE)':0x01,'LOG(UNDO)':0x02, 'LOG(ALL)':0x03}, 1,'LOGPARMS','Value of LOG parameter set by IDCAMS DEFINE/ALTER'),
('no','Character', 26,'LOGSTRID','Value of LOGSTREAMID parameter set by IDCAMS DEFINE/ALTER'),
('yes','Character', 'VL','LOKEYV','Low Key on volume'),
('no','Fixed', 4,'LRECL','Average logical record size'),
('no','Fixed', 8,'LTBACKDT','Last backup date in TOD format.'),
('no','Character', 'VL','MGMTCLAS','SMS management class'),
('yes','Character', 44,'NAME','The name of an associated entry'),
('yes','Fixed', 2,'NOBLKTRK','Number of physical blocks per track. This is the value reported by IDCAMS LISTCAT as PHYRECS/TRK'),
('yes','Fixed', 4,'NOBYTAU','Number of bytes per allocation unit'),
('yes','Fixed', 4,'NOBYTTRK','Number of bytes per track'),
('yes','Fixed', 1,'NOEXTNT','Number of extents. This is the value reported by IDCAMS LISTCAT as EXTENTS.'),
('yes','Fixed', 2,'NOTRKAU','Number of tracks per allocation unit. This is the value reported by IDCAMS LISTCAT as TRACKS/CA.'),
('no',{'Active GDS':'H', 'Deferred GDS':'N', 'Rolled-off GDS':'M', 'PDSE':'L', 'POSIX':'P', 'simple':0x00, 'Active GDS-PDSE':'I', 'Deferred GDS-PDSE':'J', 'Rolled-Off GDS-PDSE'}, 1,'NVSMATTR','Non-VSAM attribute information'),
('no',{'Open':0x80}, 1,'OPENIND','Open indicator'),
('no','Character', 8,'OWNERID','Owner of the data set'),
('no','Fixed', 2,'PASSATMP','Number of attempts to prompt for password'),
('no','Character', 8,'PASSPRMT','Password prompt code name'),
('no','Character', 32,'PASSWORD','Four 8-byte passwords (VSAM data sets only)'),
('yes','Fixed', 4,'PHYBLKSZ','Physical blocksize. This is the value reported by IDCAMS LISTCAT as PHYREC-SIZE.'),
('no','Fixed', 3,'PRIMSPAC','Primary space allocation'),
('no','Binary', 8,'RECVTIME','Recovery time, TOD value, local'),
('no','Binary', 8,'RECVTIMG','Recovery time, TOD value, GMT'),
('no',{'Upgrade':0x80, 'Alternate Index':0x40}, 1,'RGATTR','Alternate index/path attributes'),
('no',{'Undefined':(0x0F,0x00), 'BWO(TYPECICS)':(0x0F,0x01), 'BWO(TYPEIMS)':(0x0F,0x03), 1,'RLSBWO','Value of BWO parameter set by IDCAMS DEFINE/ALTER'),
('no',{'Recovery not required':(0x08,0x00), 'Recovery required':(0x08,0x08), 'Catalog is enabled for RLS':(0x04,0x00), 'Catalog is quiesced for RLS':(0x04,0x04), 'Catalog is being used in RLS mode':(0x02, 0x02)}, 1,'RLSFLAGS',''),
('no','Fixed', 3,'SCONSPAC','Secondary space allocation'),
('no','Bitstring', 1,'SECFLAGS','Security flag information x'80' means the data set has a discrete RACF profile'),
('no','Fixed', 4,'SEQSTRBA','RBA of First Sequence Set Record. maximum record number if RRDS'),
('no',{'VSAM extended format':0x80, 'VSAM compressed format':0x40, 'RLS in use':0x20, 'RLS VSAM quiesced':0x10}, 1,'SMSSFLAG','SMS FLAGS'),
('no',{'record':(0xC0,0x40), 'track':(0xC0,0x80), 'cylinder':(0xC0,0xC0)}, 1,'SPACOPTN',''),
('no','Character', 'VL','STORCLAS','SMS storage class. When the data set is not SMS-managed, the length will be no longer than 8 and the value will be hexadecimal zeroes.'),
('no','Fixed', 2,'STRIPCNT','Striping counts for striped data sets'),
('no','Fixed', 1,'STRNO','Number of concurrent requests'),
('yes','Fixed', 4,'TRACKS','Total number of tracks per volume. This field pertains only to VSAM data sets.'),
('yes','Character', 1,'TYPE','The type of an associated entry'),
('no','Fixed', 8,'UDATASIZ','User data size'),
('no','Character', 'VL','USERAREC','User authorization record'),
('no','Character', 8,'USVRMDUL','User security verification module'),
('yes',{'primary with space allocated':(0xE0,0x80), 'candidate with no space allocated':(0xE0,0x40), 'overflow volume with no space allocated':(0xE0,0x20)}, 1,'VOLFLG',''),
('yes','Character', 6,'VOLSER','Volume serial number. A VOLSER of all asterisks is the IPL volume. For a symbolic value (for example, "&xxxxx"), use the ASASYMBM service to convert the symbolic value to a valid character string.'),
('no',{'RACF discrete profile':0x80, 'Index component':0x40, 'Reusable':0x20, 'Erase specified':0x10, 'swap space':0x02, 'page space'0x01}, 1,'VSAMREUS','VSAM data set information'),
('no',(('Fixed',1,'Percentage of free CIs in CA'),('Fixed',1,'Percentage of bytes free in CI'),('Fixed',2,'Number CIs/ CA'),('Fixed',4,'Free CIs/ CA'),('Fixed',2,'Free bytes/CI'),('Fixed',4,'Number of logical records'),('Fixed',4,'Number of deleted records'),('Fixed',4,'Number of inserted records'),('Fixed',4,'Number of updated records'),('Fixed',4,'Number of retrieved records'),('Fixed',4,'non-extended: Bytes of free space. Extended: number of free CIs.'),('Fixed',4,'Number of CI splits'),('Fixed',4,'Number of CA splits'),('Fixed',4,'Number of EXCPs'),46,'VSAMSTAT','Statistics infomation for VSAM components.'),
('no',{'KDS',0x8000, 'Write check':0x4000, 'Imbed':0x2000, 'Replicate':0x1000, 'Key-range data set':0x0400, 'Spanne3d records allowed':0x0100, 'Non-unique or unique keys allowed',0x0080, 'CA-RECLAIM(NO)':0x0040, 'Statistics are not accurate':0x0020, 'LDS':0x0004, 'RRDS':0x0001}, 2,'VSAMTYPE','VSAM data set type information'),
('no',{'COMUDSIZ and UDATASIZ are invalid':0x8000,'Block level compression':0x4000}, 2,'VVRNFLGS','Extended format flags'),
('no',{'Data set can be greater than 4 GB':0x40}, 1,'XACIFLAG','Extended attribute flags'),
('yes','Fixed', 8,'XHARBA','High-allocated RBA'),
('no','Fixed', 8,'XHARBADS','Data-set high-allocated RBA'),
('yes','Fixed', 8,'XHKRBA','RBA of data control interval with high key'),
('yes','Fixed', 8,'XHURBA','High-used RBA for the volume requested'),
('no','Fixed', 8,'XHURBADS','Data-set high-used RBA'),
#Note: If you attempt to retrieve a 4-byte RBA value (such as, HARBA, HURBA, HARBADS, HURBADS, or HKRBA)
#and the value will not fit in the 4-bytes provided, that length of that returned data will be zero as shown in
# “Work Area Format Description” on page 236.
# You can either change to always request the extended fields shown above, or
#request the setting of XACIFLAG and inspect bit 1 to determine whether or not RBAs can be greater than 4 bytes. If
# so, then request the fields with the names given here.

#Library Entry Field Names
#These names are only valid for tape volume catalogs in DFSMS/MVS.
#The REP column refers to fields that can repeat when returned by CSI.
('no','Character', 8,'LCBCONID','Library console identification'),
('no','Character', 120,'LCBDESCR','Library Description'),
('no','Character', 8,'LCBDEVTP','Library device type'),
('no','Fixed', 4,'LCBEMPTY','Number of empty slots'),
('no','Character', 5,'LCBLIBID','Library Identification'),
('no','Flag', 1,'LCBLOGIC','Library logic type'),
('no','Fixed', 1020,'LCBSCRTH','Number of scratch volumes for all 255 media types'),
('no','Fixed', 4,'LCBSLOTS','Number of slots'),
('no','Fixed', 1020,'LCBTHRES','Library scratch threshold for all 255 media types'),

#Volume Entry Field Names
#These names are only valid for tape volume catalogs in DFSMS/MVS.
#The REP column refers to fields that can repeat when returned by CSI.
no Character 1 VCBCHKPT Volume checkpoint
"Y" Yes
"N" No
" " Unknown
('no','Character', 10,'VCBCRDT','Volume creation date, YYYY-MM-DD'),
('no','Group', item,'4','VCBDEVTP Volume device type'),
Fixed 1 Recording Technology
- Not defined (0)
- 18 tracks (1)
- 36 tracks (2)
- 128 tracks (3)
- 256 tracks (4)
- 384 tracks (5)
- EFMT1 (6)
Fixed 1 Media Type
- Not defined (0)
- Media 1 (1)
- Media 2 (2)
- Media 3 (3)
- Media 4 (4)
- Media 5 (5)
- Media 6 (6)
- Media 7 (7)
- Media 8 (8)
Fixed 1 Compact Type
- Not Defined (0)
- No Compaction (1)
- IDRC (2)
Fixed 1 Special Attribute
- Not Defined (0)
- Read Compatible (1)
('no','Character', 10,'VCBEDATE','Volume entry/eject date, YYYY-MM-DD'),
('no','Bitstring', 2,'VCBERRST','Volume error status (documented in member CBRVERR shipped in SYS1.MACLIB)'),
('no','Character', 10,'VCBEXPDT','Volume expiration date, YYYY-MM-DD'),
('no','Character', 44,'VCBLIBNM','Volume library name'),
('no',{'Library':'L', 'Shelf':'S', 'Unknown',' '}, 1,'VCBLOC','Volume location'),
('no','Character', 10,'VCBMOUNT','Volume last mount date, YYYY-MM-DD'),
('no','Character', 64,'VCBOWNER','Volume owner information'),
('no','Character', 8,'VCBSGRP','Volume storage group'),
('no','Character', 32,'VCBSHELF','Volume shelf location'),
('no',{'Private':'P', 'Scratch':'S', 'Unknown':' '}, 1,'VCBUATTR','Volume user attribute'),
('no','Flag', 1,'VCBWPROT','Volume write protection status'),
('no','Character', 10,'VCBWRITE','Volume last written date, YYYY-MM-DD'),
