import codecs
cp1047_oe = 'cp1047_oe'
try:
    codecs.lookup(cp1047_oe)
except LookupError:
    cp1047_oe = 'cp1047'
import ctypes
import sys
from zos.dynalloc import dynalloc

def MEM4(address, offset):
    return ctypes.c_uint.from_address(address + offset).value

def MEM8(address, offset):
    return ctypes.c_ulong.from_address(address + offset).value

def FILE_for_raw_file(raw_file):
    if hasattr(raw_file, '_file_address'): # pyan-1899 cpython pull request 35
        return raw_file._file_address()
    else:
        return MEM8(id(raw_file), sys.getsizeof(raw_file) - 4 * 8)
       
def get_cicb_from_file(job_out, mode):
    ffil = FILE_for_raw_file(job_out.buffer.raw)
    fcb = MEM8(ffil, 0)
    fsce = MEM8(fcb, 0x80)
    osio = MEM8(fsce, 0x50)
    dcb = MEM4(osio, 0x04 if mode[0] == 'w' else 0x08)
    cicb = MEM4(dcb, 0x44)
    return cicb

def get_jobid_from_cicb(cicb):
    byte_array = (ctypes.c_char * 8).from_address(cicb + 0xFC).value
    return codecs.decode(byte_array, cp1047_oe)

def submit_job(job):
    rc, results = dynalloc({"SYSOUT":"A",
                            "PROGRAM":"INTRDR",
                            "CLOSE":None,
                            "DDNAME_RETURN":None})
    if rc != 0:
        print("rc=%X, results=%r" % (rc, results))
        return list()
    mode = "wt, recfm=F, lrecl=80"
    with open("DD:%s" % results['DDNAME_RETURN'],
              mode, use_fopen=True, encoding=cp1047_oe) as job_out:
        cicb = get_cicb_from_file(job_out, mode)
        jobids = list()
        for line in job.splitlines(True):
            job_out.write(line)
            job_out.flush()
            jobid = get_jobid_from_cicb(cicb)
            if len(jobid) == 8 and (len(jobids) == 0 or jobids[-1] != jobid):
                jobids.append(jobid)
        return jobids

if __name__ == "__main__":
    myjob = "//MYJOB JOB\n//STEP EXEC PGM=IEFBR14\n"
    print(submit_job(myjob + myjob))
