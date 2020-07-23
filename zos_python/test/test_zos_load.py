import unittest
from test import support
     
import zos.load
import zos.dynalloc

test_dsn = 'AZK.AZK0120.SAZKLOAD'
test_module = 'AZKCLAPI'

test_dsn = 'PDHARR.LOADLIB'
test_module = 'CLOCK' # it is useful to test a name that is less than 8 characters long

class zos_load_test_case(unittest.TestCase):

    # load works, otherwise dynalloc would not import, and messages would not get decoded
    # this file tests zos.load.load_from_dataset

    def test_zos_load_noerror(self):
        ep = zos.load.load_from_dataset(test_dsn, test_module, verbose=True)
    def test_zos_load_open_failed(self):
        with self.assertRaises(OSError) as cm:
            mytest = zos.load.load_from_dataset("QQQ", test_module)
    def test_zos_load_bldl_failed(self):
        with self.assertRaises(OSError) as cm:
            zos.load.load_from_dataset(test_dsn, 'QQQ')
     

def test_main():
    support.run_unittest(zos_load_test_case)


if __name__ == "__main__":
    test_main()

