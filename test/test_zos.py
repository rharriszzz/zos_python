
test = None

if not test or test == 'submit':
    from zos_python.submit import submit_job

    myjob = "//MYJOB JOB\n//STEP EXEC PGM=IEFBR14\n"
    print(submit_job(myjob + myjob))

if not test or test == 'extended_status':
    from zos_python.extended_status import test_extended_status

    myjob = "//MYJOB JOB\n//STEP EXEC PGM=IEFBR14\n"
    jobid_list = submit_job(myjob)
    test_extended_status(jobid=jobid_list[0])

if not test or test == 'dataset_information':
    from zos_python.dataset_information import get_dscb1

    dsname = 'SYS1.MACLIB'
    volser = None
    print('dsname=%r volser=%r' % (dsname, volser))
    for name, value in get_dscb1(dsname, volser).items():
        print("%s=%r" % (name, value))

if not test or test == 'dataset_information':
    from zos_python.keyring import test_keyring

    test_keyring(racf_userid='*SITE*', ring_name='*', limit=3)
