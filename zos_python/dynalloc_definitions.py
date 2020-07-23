# SYS1.MACLIB(IEFZB4D2) SYS1.MACLIB(IEFSJDKY) 
#      - The character D representing Dynamic Allocation.
#        - AL for allocation,
#        - UN for unallocation,
#        - CC for concatenation,
#        - DC for deconcatenation,
#        - RI for remove in-use,
#        - DN for ddname allocation,
#        - IN for information retrieval input, and
#        - INR for information retrieval output.

DALDDNAM=0x0001 # DDNAME
DALDSNAM=0x0002 # DSNAME
DALMEMBR=0x0003 # MEMBER NAME
DALSTATS=0x0004 # DATA SET STATUS
DALNDISP=0x0005 # DATA SET NORMAL DISPOSITION
DALCDISP=0x0006 # DATA SET CONDITIONAL DISP
DALTRK  =0x0007 # TRACK SPACE TYPE
DALCYL  =0x0008 # CYLINDER SPACE TYPE
DALBLKLN=0x0009 # AVERAGE DATA BLOCK LENGTH
DALPRIME=0x000A # PRIMARY SPACE QUANTITY
DALSECND=0x000B # SECONDARY SPACE QUANTITY
DALDIR  =0x000C # DIRECTORY SPACE QUANTITY
DALRLSE =0x000D # UNUSED SPACE RELEASE
DALSPFRM=0x000E # CONTIG,MXIG,ALX SPACE FORMAT
DALROUND=0x000F # WHOLE CYLINDER (ROUND) SPACE
DALVLSER=0x0010 # VOLUME SERIAL
DALPRIVT=0x0011 # PRIVATE VOLUME
DALVLSEQ=0x0012 # VOL SEQUENCE NUMBER
DALVLCNT=0x0013 # VOLUME COUNT
DALVLRDS=0x0014 # VOLUME REFERENCE TO DSNAME
DALUNIT =0x0015 # UNIT DESCRIPTION
DALUNCNT=0x0016 # UNIT COUNT
DALPARAL=0x0017 # PARALLEL MOUNT
DALSYSOU=0x0018 # SYSOUT
DALSPGNM=0x0019 # SYSOUT PROGRAM NAME
DALSFMNO=0x001A # SYSOUT FORM NUMBER
DALOUTLM=0x001B # OUTPUT LIMIT
DALCLOSE=0x001C # UNALLOCATE AT CLOSE
DALCOPYS=0x001D # SYSOUT COPIES
DALLABEL=0x001E # LABEL TYPE
DALDSSEQ=0x001F # DATA SET SEQUENCE NUMBER
DALPASPR=0x0020 # PASSWORD PROTECTION
DALINOUT=0x0021 # INPUT ONLY OR OUTPUT ONLY
DALEXPDT=0x0022 # 2 DIGIT YEAR EXPIRATION DATE
DALRETPD=0x0023 # RETENTION PERIOD
DALDUMMY=0x0024 # DUMMY ALLOCATION
DALFCBIM=0x0025 # FCB IMAGE-ID
DALFCBAV=0x0026 # FCB FORM ALIGNMENT,IMAGE VERIFY
DALQNAME=0x0027 # QNAME ALLOCATION
DALTERM =0x0028 # TERMINAL ALLOCATION
DALUCS  =0x0029 # UNIVERSAL CHARACTER SET
DALUFOLD=0x002A # UCS FOLD MODE
DALUVRFY=0x002B # UCS VERIFY CHARACTER SET
DALDCBDS=0x002C # DCB DSNAME REFERENCE
DALDCBDD=0x002D # DCB DDNAME REFERENCE
DALBFALN=0x002E # BUFFER ALIGNMENT
DALBFTEK=0x002F # BUFFERING TECHNIQUE
DALBLKSZ=0x0030 # BLOCKSIZE
DALBUFIN=0x0031 # NUMBER OF INPUT BUFFERS
DALBUFL =0x0032 # BUFFER LENGTH
DALBUFMX=0x0033 # MAXIMUM NUMBER OF BUFFERS
DALBUFNO=0x0034 # NUMBER OF DCB BUFFERS
DALBUFOF=0x0035 # BUFFER OFFSET
DALBUFOU=0x0036 # NUMBER OF OUTPUT BUFFERS
DALBUFRQ=0x0037 # NUMBER OF GET MACRO BUFFERS
DALBUFSZ=0x0038 # LINE BUFFER SIZE
DALCODE =0x0039 # PAPER TAPE CODE
DALCPRI =0x003A # SEND/RECEIVE PRIORITY
DALDEN  =0x003B # TAPE DENSITY
DALDSORG=0x003C # DATA SET ORGANIZATION
DALEROPT=0x003D # ERROR OPTIONS
DALGNCP =0x003E # NO. OF GAM I/O BEFORE WAIT
DALINTVL=0x003F # POLLING INTERVAL
DALKYLEN=0x0040 # DATA SET KEYS LENGTH
DALLIMCT=0x0041 # SEARCH LIMIT
DALLRECL=0x0042 # LOGICAL RECORD  LENGTH
DALMODE =0x0043 # CARD READER/PUNCH MODE
DALNCP  =0x0044 # NO. READ/WRITE BEFORE CHECK
DALOPTCD=0x0045 # OPTIONAL SERVICES
DALPCIR =0x0046 # RECEIVING PCI
DALPCIS =0x0047 # SENDING PCI
DALPRTSP=0x0048 # PRINTER LINE SPACING
DALRECFM=0x0049 # RECORD FORMAT
DALRSRVF=0x004A # FIRST BUFFER RESERVE
DALRSRVS=0x004B # SECONDARY BUFFER RESERVE
DALSOWA =0x004C # TCAM USER WORK AREA SIZE
DALSTACK=0x004D # STACKER BIN
DALTHRSH=0x004E # MESSAGE QUEUE PERCENTAGE
DALTRTCH=0x004F # TAPE RECORDING TECHNOLOGY @T1C
DALPASSW=0x0050 # PASSWORD
DALIPLTX=0x0051 # IPL TEXT ID
DALPERMA=0x0052 # PERMANENTLY ALLOCATED ATTRIB
DALCNVRT=0x0053 # CONVERTIBLE ATTRIBUTE
DALDIAGN=0x0054 # OPEN/CLOSE/EOV DIAGNOSTIC TRACE
DALRTDDN=0x0055 # RETURN DDNAME
DALRTDSN=0x0056 # RETURN DSNAME
DALRTORG=0x0057 # RETURN D.S. ORGANIZATION
DALSUSER=0x0058 # SYSOUT REMOTE USER
DALSHOLD=0x0059 # SYSOUT HOLD QUEUE
DALFUNC =0x005A # D.S. TYPE FOR 3525 CARD DEVICE
DALFRID =0x005B # IMAGELIB MEMBER FOR SHARK
DALSSREQ=0x005C # SUBSYSTEM REQUEST
DALRTVOL=0x005D # RETURN VOLUME SERIAL
DALMSVGP=0x005E # MSVGP FOR 3330V
DALSSNM =0x005F # SUBSYSTEM NAME REQUEST
DALSSPRM=0x0060 # SUBSYSTEM PARAMETERS
DALPROT =0x0061 # RACF PROTECT FEATURE
DALSSATT=0x0062 # SUBSYSTEM ATTRIBUTE
DALUSRID=0x0063 # SYSOUT USER ID
DALBURST=0x0064 # BURSTER-TRIMMER-STACKER
DALCHARS=0x0065 # CHAR ARRANGEMENT TABLE
DALCOPYG=0x0066 # COPY GROUP VALUES
DALFFORM=0x0067 # FLASH FORMS OVERLAY
DALFCNT =0x0068 # FLASH FORMS OVERLAY COUNT
DALMMOD =0x0069 # COPY MODIFICATION MODULE
DALMTRC =0x006A # TABLE REFERENCE CHARACTER
DALLRECK=0x006B # LRECL IN MULT OF 1K FORMAT
DALDEFER=0x006C # DEFER MOUNT UNTIL OPEN
DALEXPDL=0x006D # 4 DIGIT YEAR EXP. DATE
DALBRTKN=0x006E # Browse token supplied
DALINCHG=0x006F # Volume Interchange Attributes
DALOVAFF=0x0070 # Tell JES to override system affinity for INTRDR
DALRTCTK=0x0071 # Return Allocation Sysout Client Token
DALKILO =0x0072 # BLKSIZE OF KILOBYTE
DALMEG  =0x0073 # BLKSIZE OF MEGABYTE
DALGIG  =0x0074 # BLKSIZE OF GIGABYTE
DALUASSR=0x0075 # Unauthorized subsystem request
DALSMSHR=0x0076 # unitname to be honored on an SMS tape library request
DALUNQDS=0x0077 # Uniquely allocated temporary data set
DALReqIEFOPZ=0x0078 # Request IEFOPZ processing
DALINSDD=0x0079 # Insulated DD request
DALNOSEC=0x007A # Bypass security checking
DALRetInfo=0x007B # Return allocation information
DALRetIEFOPZnewDSN=0x007C # Return IEFOPZ-new data set name
DALRetIEFOPZnewVol=0x007D # Return IEFOPZ-new volume serial
DALACODE=0x8001 # ACCESSIBILITY CODE
DALOUTPT=0x8002 # OUTPUT REFERENCE
DALCNTL =0x8003 # CNTL
DALSTCL =0x8004 # STORCLAS
DALMGCL =0x8005 # MGMTCLAS
DALDACL =0x8006 # DATACLAS
DALRECO =0x800B # RECORG
DALKEYO =0x800C # KEYOFF
DALREFD =0x800D # REFDD
DALSECM =0x800E # SECMODEL
DALLIKE =0x800F # LIKE
DALAVGR =0x8010 # AVGREC
DALDSNT =0x8012 # DSNTYPE
DALSPIN =0x8013 # SPIN
DALSEGM =0x8014 # SEGMENT
DALPATH =0x8017 # PATH
DALPOPT =0x8018 # PATHOPTS
DALPMDE =0x8019 # PATHMODE
DALPNDS =0x801A # PATHDISP - Normal Disposition
DALPCDS =0x801B # PATHDISP - Conditional Disposition
DALRLS  =0x801C # RLS - Record Level Sharing
DALFDAT =0x801D # FILEDATA - file organization
DALLGST =0x801F # LGSTREAM
DALDCCS =0x8020 # CCSID
DALBSLM =0x8022 # BLKSZLIM
DALKYL1 =0x8023 # KEYLABL1
DALKYL2 =0x8024 # KEYLABL2
DALKYC1 =0x8025 # KEYENCD1
DALKYC2 =0x8026 # KEYENCD2
DALEATT =0x8028 # EATTR
DALFRVL =0x8029 # FREEVOL
DALSPI2 =0x802A # SPIN second parm, SPIN INTERVAL
DALSYML =0x802B # SYMLIST ON DD
DALDSNV =0x802C # DSNTYPE version
DALMAXG =0x802D # MAXGENS
DALGDGO =0x802E # GDGORDER - GDG-all concatenation order
DALROAC =0x8030 # ROACCESS - read-only access
DALROA2 =0x8031 # ROACCESS - second parm
DALDKYL =0x8032 # Data set key label 
# KEYS FOR CONCATENATION FUNCTION
DCCDDNAM=0x0001 # DDNAMES
DCCPERMC=0x0004 # PERMANENTLY CONCATENATED
DCCINSDD=0x0079 # Concatenate Insulated DDs
# KEYS FOR DECONCATENATION FUNCTION
DDCDDNAM=0x0001 # DDNAME
DDCINSDD=0x0079 # Deconcatenate Insulated DD
# KEYS FOR INFORMATION RETRIEVAL FUNCTION
DINDDNAM=0x0001 # DDNAME
DINDSNAM=0x0002 # DSNAME
DINRTDDN=0x0004 # RETURN DDNAME
DINRTDSN=0x0005 # RETURN DSNAME
DINRTMEM=0x0006 # RETURN MEMBER NAME
DINRTSTA=0x0007 # RETURN DATA SET STATUS
DINRTNDP=0x0008 # RETURN NORMAL DISPOSITION
DINRTCDP=0x0009 # RETURN CONDITIONAL DISP
DINRTORG=0x000A # RETURN D.S. ORGANIZATION
DINRTLIM=0x000B # RETURN # TO NOT-IN-USE LIMIT
DINRTATT=0x000C # RETURN DYN. ALLOC ATTRIBUTES
DINRTLST=0x000D # RETURN LAST ENTRY INDICATION
DINRTTYP=0x000E # RETURN S.D. TYPE INDICATION
DINRELNO=0x000F # RELATIVE REQUEST NUMBER
DINRTVOL=0x0010 # Return First Volser
DINRTDDX=0x0011 # Return DDname extended
DINRLPOS=0x0012 # Return Relative Position
DINRPNAM=0x0013 # Return SYSOUT program name
DINRCNTL=0xC003 # CNTL
DINRSTCL=0xC004 # STORCLAS
DINRMGCL=0xC005 # MGMTCLAS
DINRDACL=0xC006 # DATACLAS
DINRRECO=0xC00B # RECORG
DINRKEYO=0xC00C # KEYOFF
DINRREFD=0xC00D # REFDD
DINRSECM=0xC00E # SECMODEL
DINRLIKE=0xC00F # LIKE
DINRAVGR=0xC010 # AVGREC
DINRDSNT=0xC012 # DSNTYPE
DINRSPIN=0xC013 # SPIN
DINRSEGM=0xC014 # SEGMENT
DINRPATH=0xC017 # PATH
DINRPOPT=0xC018 # PATHOPTS
DINRPMDE=0xC019 # PATHMODE
DINRPNDS=0xC01A # NORMAL PATHDISP
DINRCNDS=0xC01B # CONDITIONAL PATHDISP
DINRPCDS=0xC01B # CONDITIONAL PATHDISP
DINRFDAT=0xC01D # FILEDATA
DINRSPI2=0xC02A # SPIN interval
DINRSYML=0xC02B # SYMLIST
DINRDSNV=0xC02C # DSNTYPE version
DINRMAXG=0xC02D # MAXGENS
DINRGDGO=0xC02E # GDGORDER
DINRROAC=0xC030 # ROACCESS - first parm
DINRROA2=0xC031 # ROACCESS - second parm
DINPATH =0x8017 # PATH
# KEYS FOR REMOVE IN-USE FUNCTION
DRITCBAD=0x0001 # TCB ADDRESS
DRICURNT=0x0002 # CURRENT TASK OPTION
# KEYS FOR DDNAME ALLOCATION FUNCTION
DDNDDNAM=0x0001 # DDNAME
DDNRTDUM=0x0002 # RETURN DUMMY D.S. INDICATION
# KEYS FOR UNALLOCATION FUNCTION
DUNDDNAM=0x0001 # DDNAME
DUNDSNAM=0x0002 # DSNAME
DUNMEMBR=0x0003 # MEMBER NAME
DUNOVDSP=0x0005 # OVERRIDING DISPOSITION
DUNUNALC=0x0007 # UNALLOC OPTION
DUNREMOV=0x0008 # REMOVE OPTION
DUNOVSNH=0x000A # OVERRIDING SYSOUT NOHOLD
DUNOVCLS=0x0018 # OVERRIDING SYSOUT CLASS
DUNOVSUS=0x0058 # OVERRIDING SYSOUT NODE
DUNOVSHQ=0x0059 # OVERRIDING SYSOUT HOLD QUEUE
DUNOVUID=0x0063 # Overriding SYSOUT User ID
DUNINSDD=0x0079 # Unallocate Insulated DD
DUNNOSEC=0x007A # Bypass security checking
DUNSPIN =0x8013 # SPIN
# KEYS FOR Dynamic OUTPUT                                               
DOADDRES=0x0027 # ADDRESS
DOAFPPRM=0x0051 # AFPPARMS
DOAFPST =0x0048 # AFPPARMS
DOBUILD =0x0028 # BUILDING
DOBURST =0x0001 # BURST
DOCHARS =0x0002 # CHARS
DOCKPTLI=0x0003 # CKPTLINE
DOCKPTPA=0x0004 # CKPTPAGE
DOCKPTSE=0x0005 # CKPTSEC
DOCLASS =0x0006 # CLASS
DOCOLORM=0x003A # COLORMAP
DOCOMPAC=0x0007 # COMPACT
DOCOMSET=0x0032 # COMSETUP
DOCONTRO=0x0008 # CONTROL
DOCOPIE9=0x0009 # COPIES
DOCOPIEA=0x000A # COPIES (group values)
DOCOPYCN=0x0052 # COPYCNT
DODATACK=0x2022 # DATACK
DODDNAME=0x0054 # DDNAME
DODEFAUL=0x000B # DEFAULT
DODEPT  =0x0029 # DEPT
DODEST  =0x000C # DEST
DODPAGEL=0x0023 # DPAGELBL
DODUPLEX=0x003D # DUPLEX
DOFCB   =0x000D # FCB
DOFLASE =0x000E # FLASH (overlay name)
DOFLASF =0x000F # FLASH (count)
DOFORMD =0x001D # FORMDEF
DOFORMLN=0x003B # FORMLEN
DOFORMS =0x0010 # FORMS
DOFSSDAT=0x0047 # FSSDATA
DOGROUPI=0x0011 # GROUPID
DOINDEX =0x0012 # INDEX
DOINTRAY=0x003E # INTRAY
DOLINDEX=0x0014 # LINDEX
DOLINECT=0x0015 # LINECT
DOMAILBC=0x0049 # MAILBCC
DOMAILCC=0x004A # MAILCC
DOMAILFI=0x004B # MAILFILE
DOMAILFR=0x004C # MAILFROM
DOMAILTO=0x004D # MAILTO
DOMERGE =0x8003 # MERGE
DOMODIF6=0x0016 # MODIFY (module name)
DOMODIF7=0x0017 # MODIFY (TRC)
DONAME  =0x002D # NAME
DONOTIFY=0x002F # NOTIFY
DOXOFSTB=0x0043 # OFFSETXB
DOXOFSTF=0x0041 # OFFSETXF
DOYOFSTB=0x0044 # OFFSETYB
DOYOFSTF=0x0042 # OFFSETYF
DOOUTBIN=0x2023 # OUTBIN
DOOUTDB =0x002B # OUTDISP - NORMAL
DOOUTDC =0x002C # OUTDISP - ABNORMAL
DOOVFL  =0x0033 # OVERFLOW
DOOVRLYB=0x0040 # OVERLAYB
DOOVRLYF=0x003F # OVERLAYF
DOPAGEDE=0x001F # PAGEDEF
DOPIMSG =0x0021 # PIMSG
DOPORTNO=0x0045 # PORTNO
DOPRMODE=0x0018 # PRMODE
DOPROPTN=0x0039 # PRTOPTNS
DOPRTATT=0x0050 # PRTATTRS
DOPRTERR=0x003C # PRTERROR
DOPRTQUE=0x0038 # PRTQUEUE
DOPRTY  =0x0019 # PRTY
DOREPLYT=0x004E # REPLYTO
DORESFMT=0x0046 # RESFMT
DORETANF=0x0037 # RETAINF
DORETANS=0x0036 # RETAINS
DORETRYT=0x0034 # RETRYT
DORETRYL=0x0035 # RETRYL
DOROOM  =0x0026 # ROOM
DOSYSARE=0x0024 # SYSAREA
DOTHRESH=0x0022 # THRESHLD
DOTITLE =0x002A # TITLE
DOTRC   =0x001A # TRC
DOUCS   =0x001B # UCS
DOUSERDA=0x0031 # USERDATA
DOUSERLI=0x002E # USERLIB
DOUSERPA=0x004F # USERPATH
DOWRITER=0x001C # WRITER
# Key Constants for Output Descriptors Not Allowed Through Dynamic Output
SJOKSTNR=0x8001 # JES3STNR
SJOKMERG=DOMERGE
SJOKIPAD=0x8005 # IPADDR

KD_TYPE_VARCHAR           =0x01
KD_TYPE_Q_VARCHAR         =0x02
KD_TYPE_SYM_VARCHAR       =0x03
KD_TYPE_CHAR              =0x04
KD_TYPE_YYDDD             =0x05
KD_TYPE_YYYYDDD           =0x06
KD_TYPE_DATA              =0x07
KD_TYPE_UINT              =0x08
MAXIMUM_ALLOCATE_VOLUMES=59

# (name,part,key,max_cnt,match_seq,max_len,type) {#name,#part,#key,key,max_cnt,match_seq,max_len,type}

#(name,part,kname,key,max_cnt,match_seq,max_len,type)
KEYWORD_DEFINITION_NAMES=0
KEYWORD_DEFINITION_KEY=1
KEYWORD_DEFINITION_MAX_COUNT=2
KEYWORD_DEFINITION_MATCH_SEQ=3
KEYWORD_DEFINITION_MAX_LEN=4
KEYWORD_DEFINITION_TYPE=5
KEYWORD_DEFINITION_RETURN=6

text_keyword_definitions = {}

def build_text_keyword_definition_mapping(text_keyword_list):
    mapping = {}
    for definition in text_keyword_list:
        mapping[definition[KEYWORD_DEFINITION_KEY]] = definition
        for name in definition[KEYWORD_DEFINITION_NAMES]:
            mapping[name] = definition
    return mapping            
                              
text_keyword_definitions['allocate'] = \
  build_text_keyword_definition_mapping((
    (('DDNAME','DALDDNAM'),DALDDNAM,1,0,8,KD_TYPE_VARCHAR),
    (('DSNAME','DALDSNAM'),DALDSNAM,1,0,44,KD_TYPE_VARCHAR),
    (('MEMBER','DALMEMBR'),DALMEMBR,1,0,8,KD_TYPE_SYM_VARCHAR),
    (('STATUS','DALSTATS'),DALSTATS,1,0,1,{'OLD':1, 'MOD':2, 'NEW':4, 'SHR':8}),
    (('NORMAL_DISP','DALNDISP'),DALNDISP,1,0,1,{'UNCATLG':1, 'CATLG':2, 'DELETE':4, 'KEEP':8}),
    (('CONDITIONAL_DISP','DALCDISP'),DALCDISP,1,0,1,{'UNCATLG':1, 'CATLG':2, 'DELETE':4, 'KEEP':8}),
    (('TRACKS','DALTRK'),DALTRK,0,0,0,None),
    (('CYLINDERS','DALCYL'),DALCYL,0,0,0,None),
    (('AVERAGE_LENGTH','DALBLKLN'),DALBLKLN,1,0,3,KD_TYPE_UINT),
    (('PRIMARY','DALPRIME'),DALPRIME,1,0,3,KD_TYPE_UINT),
    (('SECONDARY','DALSECND'),DALSECND,1,0,3,KD_TYPE_UINT),
    (('DIRECTORY','DALDIR'),DALDIR,1,0,3,KD_TYPE_UINT),
    (('RELEASE','DALRLSE'),DALRLSE,0,0,0,None),
    (('SPACE_FORMAT','DALSPFRM'),DALSPFRM,1,0,1,{'ALX':2 ,'MXIG':4 ,'CONTIG':8}),
    (('ROUND','DALROUND'),DALROUND,0,0,0,None),
    (('VOLSER','DALVLSER'),DALVLSER,MAXIMUM_ALLOCATE_VOLUMES,0,6,KD_TYPE_VARCHAR),
    (('PRIVATE','DALPRIVT'),DALPRIVT,0,0,0,None),
    (('VOLSEQ','DALVLSEQ'),DALVLSEQ,1,0,2,KD_TYPE_UINT), 
    (('VOLCNT','DALVLCNT'),DALVLCNT,1,0,1,KD_TYPE_UINT),
    (('VOLREF_DS','DALVLRDS'),DALVLRDS,1,0,44,KD_TYPE_VARCHAR),
    (('UNIT','DALUNIT'),DALUNIT,1,0,8,KD_TYPE_VARCHAR),
    (('UNIT_COUNT','DALUNCNT'),DALUNCNT,1,0,1,KD_TYPE_UINT),
    (('PARALLEL','DALPARAL'),DALPARAL,0,0,0,None),
    (('SYSOUT','DALSYSOU'),DALSYSOU,1,0,1,'CHAR'), # 0 values means * 
    (('PROGRAM','DALSPGNM'),DALSPGNM,1,0,8,KD_TYPE_VARCHAR),
    (('FORM_NUMBER','DALSFMNO'),DALSFMNO,1,0,4,KD_TYPE_VARCHAR),
    (('OUTPUT_LIMIT','DALOUTLM'),DALOUTLM,1,0,3,KD_TYPE_UINT),
    (('CLOSE','DALCLOSE'),DALCLOSE,0,0,0,None),
    (('COPIES','DALCOPYS'),DALCOPYS,1,0,1,KD_TYPE_UINT),
    (('LABEL','DALLABEL'),DALLABEL,1,0,1,{'NL':0x01 ,'SL':0x02 ,'NSL':0x04 ,'SUL':0x0A ,'BLP':0x10 ,'LTM':0x21 ,'AL':0x40 ,'AUL':0x48}),
    (('DS_SEQ','DALDSSEQ'),DALDSSEQ,1,0,2,KD_TYPE_UINT),
    (('PASSWORD_PROTECT','DALPASPR'),DALPASPR,1,0,1,{'NOREAD':0x10 ,'ALLOWREAD':0x30}),
    (('INOUT_ONLY','DALINOUT'),DALINOUT,1,0,1,{'INONLY':0x40 ,'OUTONLY':0x80}),
    (('EXPIRE_YYDDD','DALEXPDT'),DALEXPDT,1,0,5,KD_TYPE_YYDDD),
    (('RETENTION_PERIOD','DALRETPD'),DALRETPD,1,0,3,KD_TYPE_UINT),
    (('DUMMY','DALDUMMY'),DALDUMMY,0,0,0,None),
    (('FCB_IMAGE','DALFCBIM'),DALFCBIM,1,0,4,KD_TYPE_VARCHAR),
    (('FCB_ALIGN_VERIFY','DALFCBAV'),DALFCBAV,1,0,1,{'VERIFY':0x04 ,'ALIGN':0x08}),
    (('QNAME','DALQNAME'),DALQNAME,1,0,17,KD_TYPE_VARCHAR),
    (('TERMINAL','DALTERM'),DALTERM,0,0,0,None),
    (('UCS','DALTERM'),DALTERM,1,0,4,KD_TYPE_VARCHAR),
    (('FOLD_MODE','DALUFOLD'),DALUFOLD,0,0,0,None),
    (('CS_IMAGE_VERIFY','DALUVRFY'),DALUVRFY,0,0,0,None),
    (('DCB_FROM_DSNAME','DALDCBDS'),DALDCBDS,1,0,44,KD_TYPE_VARCHAR),
    (('DCB_FROM_DDNAME','DALDCBDD'),DALDCBDD,1,0,8,KD_TYPE_VARCHAR),
    (('DEST_USER','DALSUSER'),DALSUSER,1,0,8,KD_TYPE_VARCHAR),
    (('HOLD','DALSHOLD'),DALSHOLD,0,0,0,None),
    (('SUBSYSTEM_NAME','DALSSNM'),DALSSNM,1,0,4,KD_TYPE_VARCHAR), # no values means default
    (('SUBSYSTEM_PARM','DALSSPRM'),DALSSPRM,254,0,67,KD_TYPE_VARCHAR),
    (('PROTECT','DALPROT'),DALPROT,0,0,0,None),
    (('DEST_USERID','DALUSRID'),DALUSRID,1,0,8,KD_TYPE_VARCHAR),
    (('BURST','DALBURST'),DALBURST,1,0,1,{'BURST':0x02 ,'CONTINUOUS':0x04}),
    (('CHARS','DALCHARS'),DALCHARS,4,0,4,KD_TYPE_VARCHAR),
    (('COPY_GROUPS','DALCOPYG'),DALCOPYG,8,0,1,KD_TYPE_UINT),
    (('FORMS_OVERLAY','DALFFORM'),DALFFORM,1,0,4,KD_TYPE_VARCHAR),
    (('FORMS_OVERLAY_COUNT','DALFCNT'),DALFCNT,1,0,1,KD_TYPE_UINT),
    (('COPY_MODIFICATION_MODULE','DALMMOD'),DALMMOD,1,0,4,KD_TYPE_VARCHAR),
    (('COPY_MODULE_TABLE','DALMTRC'),DALMTRC,1,0,1,{'FIRST':0 ,'SECOND':1 ,'THIRD':2 ,'FOURTH':3}),
    (('DEFER','DALDEFER'),DALDEFER,0,0,0,None),
    (('EXPIRE_YYYYDDD','DALEXPDL'),DALEXPDL,1,0,7,KD_TYPE_YYYYDDD),
    (('OVERRIDE_JOB_AFFINITY','DALOVAFF'),DALOVAFF,0,0,0,None),
    (('RETURN_CTOKEN','DALRTCTK'),DALRTCTK,1,0,80,'DATA'),
    (('SMS_HONOR','DALSMSHR'),DALSMSHR,0,0,0,None),
    (('ACCESS_CODE','DALACODE'),DALACODE,1,0,8,KD_TYPE_VARCHAR),
    (('OUTPUT','DALOUTPT'),DALOUTPT,128,0,26,KD_TYPE_VARCHAR),
    (('CNTL','DALCNTL'),DALCNTL,1,0,26,KD_TYPE_VARCHAR),
    (('STORAGE_CLASS','DALSTCL'),DALSTCL,1,0,8,KD_TYPE_VARCHAR),
    (('MANAGEMENT_CLASS','DALMGCL'),DALMGCL,1,0,8,KD_TYPE_VARCHAR),
    (('DATA_CLASS','DALDACL'),DALDACL,1,0,8,KD_TYPE_VARCHAR),
    (('VSAM_RECORD_ORGANIZATION','DALRECO'),DALRECO,1,0,1,{'KS':0x80 ,'ES':0x80 ,'RR':0x20 ,'LS':0x10}),
    (('VSAM_KEY_OFFSET','DALKEYO'),DALKEYO,1,0,4,KD_TYPE_UINT),
    (('REFER_DDNAME','DALREFD'),DALREFD,1,0,44,KD_TYPE_VARCHAR),
    (('COPY_PROFILE','NAME','DALSECM'),DALSECM,1,1,255,KD_TYPE_VARCHAR),
    (('COPY_PROFILE','GENERIC','DALSECM'),DALSECM,2,2,1,{'GENERICPROFILE':0x80}),
    (('COPY_MODEL','DALLIKE'),DALLIKE,1,0,44,KD_TYPE_VARCHAR),
    (('AVERAGE_RECORD','DALAVGR'),DALAVGR,1,0,1,{'1':0x80 ,'1000':0x40 ,'1000000':0x20}),
    (('DATASET_NAME_TYPE','DALDSNT'),DALDSNT,1,0,1,
     {'PDSE':0x80 ,'PDS':0x40 ,'PIPE':0x20 ,'HFS':0x10 ,'EXTREQ':0x08 ,'EXTPREF':0x04 ,'BASIC':0x02 ,'LARGE':0x01}),
    (('SPIN','DALSPIN'),DALSPIN,1,0,1,{'UNALLOCATE':0x80 ,'ENDOFJOB':0x40}),
    (('SEGMENT_SPIN','DALSEGM'),DALSEGM,1,0,4,KD_TYPE_UINT),
    (('PATH','DALPATH'),DALPATH,1,0,255,KD_TYPE_VARCHAR),
    (('PATH_OPTIONS','DALPOPT'),DALPOPT,1,0,4,KD_TYPE_UINT),
    (('PATH_MODE','DALPMDE'),DALPMDE,1,0,4,KD_TYPE_UINT),
    (('PATH_NORMAL_DISP','DALPNDS'),DALPNDS,1,0,1,{'DELETE':4, 'KEEP':8}),
    (('PATH_CONDITIONAL_DISP','DALPCDS'),DALPCDS,1,0,1,{'DELETE':4, 'KEEP':8}),
    (('RLS','DALRLS'),DALRLS,1,0,1,{'NRI':0x80 ,'CR':0x40 ,'CRE':0x20}),
    (('FILE_DATA_ORGANIZATION','DALFDAT'),DALFDAT,1,0,1,{'BINARY':0x80 ,'NL':0x40 ,'RECORD':0x20}),
    (('VSAM_RLS_LOG_STREAM_PREFIX','DALLGST'),DALLGST,1,0,44,KD_TYPE_VARCHAR),
    (('TAPE_CCSID','DALDCCS'),DALDCCS,1,0,4,KD_TYPE_UINT),
    (('BLOCK_SIZE_LIMIT','DALBSLM'),DALBSLM,1,0,10,KD_TYPE_VARCHAR),
    (('KEY_LABEL_1','DALKYL1'),DALKYL1,1,0,64,KD_TYPE_VARCHAR),
    (('KEY_LABEL_2','DALKYL2'),DALKYL2,1,0,64,KD_TYPE_VARCHAR),
    (('KEY_ENCODE_1','DALKYC1'),DALKYC1,1,0,1,KD_TYPE_CHAR),
    (('KEY_ENCODE_2','DALKYC2'),DALKYC2,1,0,1,KD_TYPE_CHAR),
    (('EXTENDED_ATTRIBUTES_ALLOWED','DALEATT'),DALEATT,1,0,1,{'NO':0x01 ,'OPTIONAL':0x02}),
    (('FREEVOL','DALFRVL'),DALFRVL,1,0,1,{'EOJ':0x01 ,'READ':0x02}),
    (('SPIN_INTERVAL','DALSPI2'),DALSPI2,1,0,8,KD_TYPE_VARCHAR),
    (('SYMLIST','DALSYML'),DALSYML,128,0,255,KD_TYPE_VARCHAR),
    (('DSNTYPE_LIBRARY_VERSION','DALDSNV'),DALDSNV,1,0,1,KD_TYPE_UINT),
    (('MAX_PDSE_MEMBER_GENERATIONS','DALMAXG'),DALMAXG,1,0,4,KD_TYPE_UINT),
    (('GDG_CONCATENATION_ORDER','DALGDGO'),DALGDGO,1,0,1,{'USECATLG':0x80 ,'LIFO':0x40 ,'FIFO':0x20}),
    (('ROACCESS','DALROAC'),DALROAC,1,1,1,{'ALLOW':0x01 ,'DISALLOW':0x02}),
    (('ROACCESS2','DALROA2'),DALROA2,1,2,1,{'EXTLOCK':0x01 ,'TRKLOCK':0x02}),
    (('ENCRYPTION_KEY_LABEL','DALDKYL'),DALDKYL,1,0,64,KD_TYPE_VARCHAR),
    # non-JCL text units, including those that return information
    (('PASSWORD', 'DALPASSW'), DALPASSW,1,0,8,KD_TYPE_VARCHAR),
    (('PERMANENTLY_ALLOCATED','DALPERMA'), DALPERMA,0,0,0,None),
    (('CONVERTABLE_ATTRIBUTE','DALCNVRT'), DALCNVRT,0,0,0,None), # doc says this is the default unless DALPERMA is supplied
    (('DDNAME_RETURN','DALRTDDN'),DALRTDDN,1,0,8,KD_TYPE_VARCHAR,'RETURN'),
    (('DSNAME_RETURN','DALRTDSN'),DALRTDDN,1,0,44,KD_TYPE_VARCHAR,'RETURN'),
    (('DSORG_RETURN','DALRTORG'),DALRTORG,1,0,2,
     {None:0x0000, 'TR':0x0004,'VSAM':0x0008,'TQ':0x0020,'TX':0x0040,'GS':0x0080,
      'PO':0x0200,'POU':0x0300,'MQ':0x0400,'CQ':0x0800,'CX':0x1000,'DA':0x2000,
      'DAU':0x2100,'PS':0x4000,'PSU':0x4100,'IS':0x8000,'ISU':0x8100},'RETURN'),
    (('SUBSYSTEM_REQUEST','DALSSREQ'),DALSSREQ,1,0,4,KD_TYPE_VARCHAR),
    (('VOLUME_SERIAL_RETURN','DALRTVOL'),DALRTVOL,1,0,6,KD_TYPE_VARCHAR,'RETURN')
    ))

# Spool data set browse token specification - Key = '006E'
# DALBRTKN specifies a spool data set browse token that contains information
# about a JES2 spool data set that a user asks to browse. In addition to parameters
# about the spool data set, the token also contains parameters that you can use with
# the System Authorization Facility to check the user's browse authorization.
# 
# When you code DALBRTKN, # must be 7. Mapping macro IAZBTOKP maps the
# length and parameter portion of this text unit. For a description of the IAZBTOKP
# mapping macro, see z/OS MVS Data Areas in the z/OS Internet library
# (www.ibm.com/systems/z/os/zos/library/bkserv).
# Example: Define the spool data set browse token in IAZBTOKP as follows:
# v BTOK is the name of the spool data set browse token (BTOKID).
# v 1 is the version number of the parameter list for BTOK (BTOKVERNM).
# v 01001302 is the I/O table (IOT) module track record (MTTR) pointer
# (BTOKIOTP).
# v A9BC2033 is the spool data set job key (BTOKJKEY).
# v 017E is the ASID of the job that owns the spool data set (BTOKASID).
# v IBMUSER is the RECVR userid you can use on a SAF call to check the authority
# of the browse request (BTOKRCID).
# v DATA SET BROWSE is the LOGSTR data associated with IBMUSER
# (BTOKLOG5).
# KEY # LEN1 PARM1 LEN2 PARM2 ... LEN7 PARM7
# 006E 007 IAZBTOKP DSECT containing the values associated with BTOK
# Using the IAZBTOKP field names, the result is:
# KEY # BTOKPL1 BTOKID BTOKPL2 BTOKVRNM BTOKPL3 BTOKIOTP
# 006E 0007 0004 C2E3D6D2 0002 0001 0004 01001302
# BTOKPL4 BTOKJKEY BTOKPL5 BTOKASID BTOKPL6 BTOKRCID
# 0004 A9BC2033 0002 017E 0008 C9C2D4E4 C2C5D940
# BTOKPL7 BTOKLOGS
# 00FF 0FC4C1E3 C140E2C5 C340C2D9 D6E6E2C5

# Volume interchange specification - Key = '006F'
# DALINCHG specifies the media type and track recording technique required for
# system-managed tape library allocation.
# Whenever possible, IBM suggests that you use an installation-defined DATACLAS
# construct name to control cartridge media type and track recording technique. Use
# this key only when it is not possible to use a pre-defined DATACLAS construct
# because of the dynamic nature of the program and because the program must
# control the media type and track recording technique. Contact your storage
# administrator before using this key.
# Note: To specify DALINCHG, your program must be APF-authorized, in
# supervisor state, or running in PSW key 0-7. The specification of DALINCHG will
# be ignored if a non-system-managed tape volume is allocated.
# When you code this key, # must be one, but LEN and PARM can be either 1 byte
# or 2 bytes in length. PARM must contain one of the following values:
# ... lots of stuff ...

# Subsystem request specification - Key = '0075'
# DALUASSR requests that a subsystem data set be allocated and, optionally,
# specifies the name of the subsystem for which the data set is to be allocated.
# This request is similar to the DALSSREQ request, but can be used by unauthorized
# callers.
# 
# When you code DALUASSR without specifying a subsystem name, # must be zero
# and LEN and PARM are not specified. The data set is then allocated to the primary
# subsystem.
# When you code the subsystem name in the DALUASSR key, # must be one, LEN is
# the length of the subsystem name, up to a maximum of 4, and PARM contains the
# subsystem name.
# Example 1: To request a subsystem data set for the primary subsystem, code:
# KEY # LEN PARM
# 0075 0000 - -
# Example 2: To request a subsystem data set for JES2, code:
# KEY # LEN PARM
# 0075 0001 0004 D1 C5 E2 F2

# Uniquely allocated temporary data set - Key = '0077'
# DALUNQDS indicates that a temporary data set is being allocated and that the
# address space allocating the data set will only allocate the specified data set name,
# or generated data set name, to the DD currently being allocated, and no other DD.
# Dynamic allocation normally tracks temporary data set names when they are
# allocated and uses this information to avoid deleting a temporary data set more
# than once when the data set is allocated multiple times. Use of this text unit
# indicates that the dynamic allocation caller will ensure that the temporary data set
# is only allocated once and that the system can avoid this processing.
# When you code DALUNQDS, # must be zero. LEN and PARM are not specified.
# Example: To indicate that a temporary data set is uniquely allocated:
# KEY # LEN PARM
# 0077 0000 - -

# Request IEFOPZ processing - Key = '0078'
# DALReqIEFOPZ requests that IEFOPZ processing be performed on the data set
# provided by DALDSNAM (and, optionally, by DALVLSER).
# When you code this key, # must be zero, and LEN and PARM are not specified.
# Example: To request IEFOPZ processing, code:
# KEY # LEN PARM
# 0078 0000 - -

# Insulated DD request - Key = '0079'
# DALINSDD indicates that the insulated DD attribute is to be assigned to this
# allocation.
# For a description of this key, see “Insulated DD attribute” on page 549. When you
# code this key, # must be zero, and LEN and PARM are not specified.
# DALINSDD is mutually exclusive with the DALCNVRT (X'0053') and DALCLOSE
# (X'001C') text units.
# Use of DALINSDD implies that the DD is permanently allocated.
# This text unit is available on z/OS 1.13 and later systems with APAR OA47824
# installed. When this support is available, the JESIBSAV flag in the JESCT is on. See
# the IEFJESCT macro for usage in formation.
# Note: To specify DALINSDD, your program must be APF-authorized, in
# supervisor state, or running with PSW key 0 - 7.
# Example: To specify assignment of the insulated DD attribute, code:
# KEY # LEN PARM
# 0079 0000 - -

# Return allocation information - Key = '007B'
# DALRetInfo requests indications of the attributes assigned to the specified
# resource.
# When you code this key, # and LEN must be 1, and PARM is a one-byte field.
# Upon return to your program, PARM is set as follows:
# Bit Meaning
# 0 ON if IEFOPZ processing found a match for this allocation.
# 1-7 Not an intended programming interface.
# Example: To request allocation information, code:
# KEY # LEN PARM
# 007B 0001 1 -
# If IEFOPZ processing was performed, PARM contains the following data upon
# return:
# KEY # LEN PARM
# 007B 0001 1 80

# Return IEFOPZ-New data set name - Key = '007C'
# DALRetIEFOPZNewDSN requests that the IEFOPZ-New data set name from
# IEFOPZ processing be returned to the caller.
# When you code this key, # must be 1, and LEN must be at least the length of the
# dsname (and can be longer, up to a maximum of 44 characters). The PARM field
# must be the length specified by the LEN value.
# Dynamic allocation places the allocated dsname in PARM and updates LEN to the
# length of the returned dsname. If no IEFOPZ-New data set was added, the # field
# is set to 0 on output, and the LEN and PARM fields contain no valid data.
# Example: To request that IEFOPZ-New data set name be returned, code:
# KEY # LEN PARM
# 007C 0001 002C --------
# If an IEFOPZ-New data set is processed, this specification is updated for the
# allocation of the dsname ABC, as follows:
# KEY # LEN PARM
# 007C 0001 0003 C1C2C3
# If an IEFOPZ-New data set is not processed, the specification is updated, as
# follows:
# KEY # LEN PARM
# 007C 0000 ???? ????????????

# Return IEFOPZ-New data set volume serial number - Key = '007D'
# DALRetIEFOPZNewVol requests that the volume serial number associated with the
# IEFOPZ-New data set from IEFOPZ processing be returned to the caller.
# When you code th is key, # must be 1, LEN must be 6, and PARM is a six-byte
# field.
# If no IEFOPZ-New data set was added, the # field is set to 0 on output, and the
# LEN and PARM fields contain no valid data.
# Note: Only the first volume serial number of a multiple-volume data set is
# returned.
# Example: To request that the IEFOPZ-New volume serial number be returned,
# code:
# KEY # LEN PARM
# 007D 0001 0006 ------
# If an IEFOPZ-New data set is processed, this specification is updated for the
# allocation of the IEFOPZ-New data set on volume 123456, as follows:
# KEY # LEN PARM
# 007D 0001 0006 F1F2F3F4F5F6
# If an IEFOPZ-New data set is not processed, the specification is updated, as
# follows:
# KEY # LEN PARM
# 007D 0000 ???? ????????????


# Dynamic unallocation text units
# Use verb code 02 and the text unit keys listed in Table 88 and described on the
# following pages to request dynamic unallocation processing by DYNALLOC. To
# deallocate a resource, you must specify either the DUNDDNAM key, the
# DUNDSNAM key, or the DUNPATH key.
# Table 88. Verb code 02 (dynamic unallocation) – Text unit keys, mnemonics, and functions
# Hex text
# unit key
# Mnemonic DYNALLOC function
# 0001 DUNDDNAM Specifies the ddname of the resource to be
# deallocated.
# 0002 DUNDSNAM Specifies the data set to be deallocated.
# 0003 DUNMEMBR Specifies the PDS member to be deallocated.
# 0005 DUNOVDSP Specifies an overriding disposition for the data set to
# be unallocated.
# 0007 DUNUNALC Specifies deallocation even if the resource has the
# permanently allocated attribute.
# 0008 DUNREMOV Specifies removal of

text_keyword_definitions['unallocate'] = \
  build_text_keyword_definition_mapping((
      (('DDNAME','DUNDDNAM'),DUNDDNAM,1,0,8,KD_TYPE_VARCHAR),
      (('DSNAME','DUNDSNAM'),DUNDSNAM,1,0,44,KD_TYPE_VARCHAR),
      (('MEMBER','DUNMEMBR'),DUNMEMBR,1,0,8,KD_TYPE_VARCHAR),
      (('OVERRIDE_DISP','DUNOVDSP'),DUNOVDSP,1,0,1,{'UNCATLG':1, 'CATLG':2, 'DELETE':4, 'KEEP':8}),
      (('UNALLOCATE','DUNUNALC'),DUNUNALC,0,0,0,None),
      (('REMOVE','DUNREMOV'),DUNREMOV,0,0,0,None)
      # there are more
  ))

text_keyword_definitions['concatenate'] = \
  build_text_keyword_definition_mapping((
      (('DDNAMES','DCCDDNAM'),DCCDDNAM,1635,0,8,KD_TYPE_VARCHAR),
      (('PERMANENTLY_CONCATENATED','DCCPERMC'),DCCPERMC,0,0,0,None)))

text_keyword_definitions['deconcatenate'] = \
  build_text_keyword_definition_mapping((
      (('DDNAMES','DDCDDNAM'),DDCDDNAM,1,0,8,KD_TYPE_VARCHAR),))

text_keyword_definitions['information_retrieval'] = \
  build_text_keyword_definition_mapping((
      (('DDNAME','DINDDNAM'),DINDDNAM,1,0,8,KD_TYPE_VARCHAR),
      (('DSNAME','DINDSNAM'),DINDSNAM,1,0,8,KD_TYPE_VARCHAR),
      (('PATH', 'DINPATH'),DINPATH,1,0,255,KD_TYPE_VARCHAR),
      (('RELATIVE REQUEST NUMBER', 'DINRELNO'),DINRELNO,1,0,2,KD_TYPE_UINT),

      (('RETURN DDNAME', 'DINRTDDN'),DINRTDDN,1,0,8,KD_TYPE_VARCHAR,'RETURN'),
      (('RETURN DSNAME', 'DINRTDSN'),DINRTDSN,1,0,44,KD_TYPE_VARCHAR,'RETURN'),
      (('RETURN MEMBER NAME', 'DINRTMEM'),DINRTMEM,1,0,8,KD_TYPE_VARCHAR,'RETURN'),
      (('RETURN DATA SET STATUS', 'DINRTSTA'),DINRTSTA,'RETURN'),
      (('RETURN NORMAL DISPOSITION', 'DINRTNDP'),DINRTNDP,1,0,1,{'UNCATLG':1, 'CATLG':2, 'DELETE':4, 'KEEP':8},'RETURN'),
      (('RETURN CONDITIONAL DISP', 'DINRTCDP'),DINRTCDP,1,0,1,{'UNCATLG':1, 'CATLG':2, 'DELETE':4, 'KEEP':8},'RETURN'),
      (('RETURN D.S. ORGANIZATION', 'DINRTORG'),DINRTORG,'RETURN'),
      (('RETURN NUMBER TO NOT-IN-USE LIMIT', 'DINRTLIM'),DINRTLIM,'RETURN'),
      (('RETURN DYN. ALLOC ATTRIBUTES', 'DINRTATT'),DINRTATT,'RETURN'),
      (('RETURN LAST ENTRY INDICATION', 'DINRTLST'),DINRTLST,1,0,1,{'LAST':0x80},'RETURN'),
      (('RETURN S.D. TYPE INDICATION', 'DINRTTYP'),DINRTTYP,'RETURN'),
      (('RETURN FIRST VOLSER', 'DINRTVOL'),DINRTVOL,'RETURN'),
      (('RETURN DDNAME EXTENDED', 'DINRTDDX'),DINRTDDX,1,0,8,KD_TYPE_VARCHAR,'RETURN'),
      (('RETURN RELATIVE POSITION','DINRLPOS'),DINRLPOS,1,0,2,KD_TYPE_UINT,'RETURN'),
      (('RETURN CNTL', 'DINRCNTL'),DINRCNTL,'RETURN'),
      (('RETURN STORCLAS', 'DINRSTCL'),DINRSTCL,'RETURN'),
      (('RETURN MGMTCLAS', 'DINRMGCL'),DINRMGCL,'RETURN'),
      (('RETURN DATACLAS', 'DINRDACL'),DINRDACL,'RETURN'),
      (('RETURN RECORG', 'DINRRECO'),DINRRECO,'RETURN'),
      (('RETURN KEYOFF', 'DINRKEYO'),DINRKEYO,'RETURN'),
      (('RETURN REFDD', 'DINRREFD'),DINRREFD,'RETURN'),
      (('RETURN SECMODEL', 'DINRSECM'),DINRSECM,'RETURN'),
      (('RETURN LIKE', 'DINRLIKE'),DINRLIKE,'RETURN'),
      (('RETURN AVGREC', 'DINRAVGR'),DINRAVGR,'RETURN'),
      (('RETURN DSNTYPE', 'DINRDSNT'),DINRDSNT,'RETURN'),
      (('RETURN SPIN', 'DINRSPIN'),DINRSPIN,'RETURN'),
      (('RETURN SEGMENT', 'DINRSEGM'),DINRSEGM,'RETURN'),
      (('RETURN PATH', 'DINRPATH'),DINRPATH,1,0,255,KD_TYPE_VARCHAR,'RETURN'),
      (('RETURN PATHOPTS', 'DINRPOPT'),DINRPOPT,'RETURN'),
      (('RETURN PATHMODE', 'DINRPMDE'),DINRPMDE,'RETURN'),
      (('RETURN NORMAL PATHDISP', 'DINRPNDS'),DINRPNDS,'RETURN'),
      (('RETURN CONDITIONAL PATHDISP', 'DINRCNDS'),DINRCNDS,'RETURN'),
      (('RETURN CONDITIONAL PATHDISP', 'DINRPCDS'),DINRPCDS,'RETURN'),
      (('RETURN FILEDATA', 'DINRFDAT'),DINRFDAT,'RETURN'),
      (('RETURN SPIN INTERVAL', 'DINRSPI2'),DINRSPI2,'RETURN'),))

text_keyword_definitions['output'] = \
  build_text_keyword_definition_mapping((
    (('ADDRESS','DOADDRES'),DOADDRES,4,0,60,KD_TYPE_VARCHAR),
    (('AFPPARMS','DOAFPPRM'),DOAFPPRM,1,0,54,KD_TYPE_VARCHAR),
    (('BUILDING','DOBUILD'),DOBUILD,1,0,60,KD_TYPE_VARCHAR),
    (('BURST','DOBURST'),DOBURST,1,0,1,{'NO':0x80,'YES':0x40}),
    (('CHARS','DOCHARS'),DOCHARS,4,0,4,KD_TYPE_VARCHAR),
    (('CKPTLINE','DOCKPTLI'),DOCKPTLI,1,0,2,KD_TYPE_UINT),
    (('CKPTPAGE','DOCKPTPA'),DOCKPTPA,1,0,2,KD_TYPE_UINT),
    (('CKPTSEC','DOCKPTSE'),DOCKPTSE,1,0,2,KD_TYPE_UINT),
    (('CLASS','DOCLASS'),DOCLASS,1,0,1,KD_TYPE_VARCHAR),
    (('COLORMAP','DOCOLORM'),DOCOLORM,1,0,8,KD_TYPE_VARCHAR),
    (('COMPACT','DOCOMPAC'),DOCOMPAC,1,0,8,KD_TYPE_VARCHAR),
    (('COMSETUP','DOCOMSET'),DOCOMSET,1,0,8,KD_TYPE_VARCHAR),
    (('CONTROL','DOCONTRO'),DOCONTRO,1,0,1,{'SINGLE':0x80 ,'DOUBLE':0x40 ,'TRIPLE':0x20 ,'PROGRAM':0x10}),
    (('COPIES','COUNT','DOCOPIE9'),DOCOPIE9,1,0,1,KD_TYPE_UINT),
    (('COPIES','GROUPS','DOCOPIEA'),DOCOPIEA,8,0,1,KD_TYPE_UINT),
    (('DATACK','DODATACK'),DODATACK,1,0,1,{'BLOCK':0x00 ,'UNBLOCK':0x80 ,'BLKCHAR':0x81 ,'BLKPOS':0x82}),
    (('DEFAULT','DODEFAUL'),DODEFAUL,1,0,1,{'NO':0x80,'YES':0x40}),
    (('DEPT','DODEPT'),DODEPT,1,0,60,KD_TYPE_VARCHAR),
    (('DEST','DODEST'),DODEST,1,0,127,KD_TYPE_VARCHAR),
    (('DPAGELBL','DODPAGEL'),DODPAGEL,1,0,1,{'NO':0x80,'YES':0x40}),
    (('DUPLEX','DODUPLEX'),DODUPLEX,1,0,1,{'NO':0x80 ,'NORMAL':0x40 ,'TUMBLE':0x20}),
    (('FCB','DOFCB'),DOFCB,1,0,4,KD_TYPE_VARCHAR),
    (('FLASH','OVERLAY','DOFLASE'),DOFLASE,1,0,4,KD_TYPE_VARCHAR),
    (('FLASH','COUNT','DOFLASF'),DOFLASF,1,0,1,KD_TYPE_UINT),
    (('FORMDEF','DOFORMD'),DOFORMD,1,0,6,KD_TYPE_VARCHAR),
    (('FORMLEN','DOFORMLN'),DOFORMLN,1,0,10,KD_TYPE_VARCHAR),
    (('FORMS','DOFORMS'),DOFORMS,1,0,8,KD_TYPE_VARCHAR),
    (('FSSDATA','DOFSSDAT'),DOFSSDAT,1,0,127,KD_TYPE_VARCHAR),
    (('GROUPID','DOGROUPI'),DOGROUPI,1,0,8,KD_TYPE_VARCHAR),
    (('INDEX','DOINDEX'),DOINDEX,1,0,1,KD_TYPE_UINT),
    (('INTRAY','DOINTRAY'),DOINTRAY,1,0,3,KD_TYPE_UINT),
    (('IPADDR','SJOKIPAD'),SJOKIPAD,1,0,127,KD_TYPE_VARCHAR),
    (('LINDEX','DOLINDEX'),DOLINDEX,1,0,1,KD_TYPE_UINT),
    (('LINECT','DOLINECT'),DOLINECT,1,0,1,KD_TYPE_UINT),
    (('MAILBCC','DOMAILBC'),DOMAILBC,32,0,60,KD_TYPE_VARCHAR),
    (('MAILCC','DOMAILCC'),DOMAILCC,32,0,60,KD_TYPE_VARCHAR),
    (('MAILFILE','DOMAILFI'),DOMAILFI,1,0,60,KD_TYPE_VARCHAR),
    (('MAILFROM','DOMAILFR'),DOMAILFR,1,0,60,KD_TYPE_VARCHAR),
    (('MAILTO','DOMAILTO'),DOMAILTO,32,0,60,KD_TYPE_VARCHAR),
    (('MODIFY','MODULE','DOMODIF6'),DOMODIF6,1,0,4,KD_TYPE_VARCHAR),
    (('MODIFY','TRC','DOMODIF7'),DOMODIF7,1,0,1,KD_TYPE_UINT),
    (('NAME','DONAME'),DONAME,1,0,60,KD_TYPE_VARCHAR),
    (('NOTIFY','DONOTIFY'),DONOTIFY,4,0,17,KD_TYPE_VARCHAR),
    (('OFFSETXB','DOXOFSTB'),DOXOFSTB,10,0,13,KD_TYPE_VARCHAR),
    (('OFFSETXF','DOXOFSTF'),DOXOFSTF,10,0,13,KD_TYPE_VARCHAR),
    (('OFFSETYB','DOYOFSTB'),DOYOFSTB,10,0,13,KD_TYPE_VARCHAR),
    (('OFFSETYF','DOYOFSTF'),DOYOFSTF,10,0,13,KD_TYPE_VARCHAR),
    (('OUTBIN','DOOUTBIN'),DOOUTBIN,1,0,4,KD_TYPE_UINT),
    (('OUTDISP','NORMAL','DOOUTDB'),DOOUTDB,1,0,1,{'WRITE':0x80 ,'HOLD':0x40 ,'KEEP':0x20 ,'LEAVE':0x10 ,'PURGE':0x08}),
    (('OUTDISP','ABNORMAL','DOOUTDC'),DOOUTDC,1,0,1,{'WRITE':0x80 ,'HOLD':0x40 ,'KEEP':0x20 ,'LEAVE':0x10 ,'PURGE':0x08}),
    (('OVERLAYB','DOOVRLYB'),DOOVRLYB,1,0,8,KD_TYPE_VARCHAR),
    (('OVERLAYF','DOOVRLYF'),DOOVRLYF,1,0,8,KD_TYPE_VARCHAR),
    (('OVFL','DOOVFL'),DOOVFL,1,0,1,{'ON':0x80,'OFF':0x40}),
    (('PAGEDEF','DOPAGEDE'),DOPAGEDE,1,0,6,KD_TYPE_VARCHAR),
    (('PIMSG','DOPIMSG'),DOPIMSG,2,1,1,{'NO':0x80,'YES':0x40}),
    (('PIMSG','DOPIMSG'),DOPIMSG,2,2,2,KD_TYPE_UINT),
    (('PORTNO','DOPORTNO'),DOPORTNO,1,0,2,KD_TYPE_UINT),
    (('PRMODE','DOPRMODE'),DOPRMODE,1,0,8,KD_TYPE_VARCHAR),
    (('PRTATTRS','DOPRTATT'),DOPRTATT,1,0,127,KD_TYPE_VARCHAR),
    (('PRTOPTNS','DOPROPTN'),DOPROPTN,1,0,16,KD_TYPE_VARCHAR),
    (('PRTERROR','DOPRTERR'),DOPRTERR,1,0,1,{'QUIT':0x80 ,'HOLD':0x40 ,'DEFAULT':0x20}),
    (('PRTQUEUE','DOPRTQUE'),DOPRTQUE,1,0,127,KD_TYPE_VARCHAR),
    (('PRTY','DOPRTY'),DOPRTY,1,0,1,KD_TYPE_UINT),
    (('REPLYTO','DOREPLYT'),DOREPLYT,1,0,60,KD_TYPE_VARCHAR),
    (('RESFMT','DORESFMT'),DORESFMT,1,0,1,{'P249':0x80 ,'P300':0x40}),
    (('RETAINF','DORETANF'),DORETANF,1,0,10,KD_TYPE_VARCHAR),
    (('RETAINS','DORETANS'),DORETANS,1,0,10,KD_TYPE_VARCHAR),
    (('RETRYL','DORETRYL'),DORETRYL,1,0,3,KD_TYPE_UINT),
    (('RETRYT','DORETRYT'),DORETRYT,1,0,8,KD_TYPE_VARCHAR),
    (('ROOM','DOROOM'),DOROOM,1,0,60,KD_TYPE_VARCHAR),
    (('SYSAREA','DOSYSARE'),DOSYSARE,1,0,1,{'NO':0x80,'YES':0x40}),
    (('THRESHLD','DOTHRESH'),DOTHRESH,1,0,4,KD_TYPE_UINT),
    (('TITLE','DOTITLE'),DOTITLE,1,0,60,KD_TYPE_VARCHAR),
    (('TRC','DOTRC'),DOTRC,1,0,1,{'NO':0x80,'YES':0x40}),
    (('UCS','DOUCS'),DOUCS,1,0,4,KD_TYPE_VARCHAR),
    (('USERDATA','DOUSERDA'),DOUSERDA,16,0,60,KD_TYPE_VARCHAR),
    (('USERLIB','DOUSERLI'),DOUSERLI,8,0,44,KD_TYPE_VARCHAR),
    (('USERPATH','DOUSERPA'),DOUSERPA,8,0,255,KD_TYPE_VARCHAR),
    (('WRITER','DOWRITER'),DOWRITER,1,0,8,KD_TYPE_VARCHAR)))