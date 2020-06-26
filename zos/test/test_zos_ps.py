
import unittest
from test import support
from os import getpid
from zos.ps import ps

#def ps_test(pid=0, asid=0, loginname=None):
#    for result in ps(pid=pid, asid=asid, loginname=loginname):
#        print(repr(result))
#
#with open("/u/pdharr/#zd#", "r") as file_in1:
#    with open("/u/pdharr/#a#", "r") as file_in2:
#        ps_test(pid=os.getpid())
#ps_test(loginname=os.getenv('USER'))

class zos_ps_test_case(unittest.TestCase):
    
    def test_ps(self):
        pid = getpid()
        result = [data for data in ps(pid=pid)]
        self.assertEqual(1, len(result))
        self.assertEqual(pid, result[0]['PROCESS']['process id'])
     

def test_main():
    support.run_unittest(zos_ps_test_case)


if __name__ == "__main__":
    test_main()

