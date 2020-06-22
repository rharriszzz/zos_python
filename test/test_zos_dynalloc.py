import unittest
from test import support
import zos.dynalloc

jcl_library = "PDHARR.JCL"
jcl_member = 'TRSM'

load_library = "PDHARR.LOADLIB"

class zos_dynalloc_test_case(unittest.TestCase):
    
    def test_dynalloc_success(self):
        rc, results = zos.dynalloc.dynalloc({"DSNAME":jcl_library, "MEMBER":jcl_member, "STATUS":"SHR", "DDNAME_RETURN":None})
        self.assertEqual(0, rc)
        self.assertIn("DDNAME_RETURN", results)
        ddname = results["DDNAME_RETURN"]
        rc, results = zos.dynalloc.dynunalloc({"DDNAME":ddname})
        self.assertEqual(0, rc)

    def test_dynalloc_failure(self):
        rc, results = zos.dynalloc.dynalloc({"DSNAME":load_library, "STATUS":"SHR", "DDNAME_RETURN":None})
        ddname = results['DDNAME_RETURN']
        messages = []
        def save_message(message):
            messages.append(message)
        rc, results = zos.dynalloc.dynconcatenate({"DDNAMES":['STEPLIB', ddname]}, message_function=save_message)
        self.assertNotEqual(0, rc)
        self.assertEqual(2, len(messages))
        self.assertEqual('concatenate failed, return code=12, error=0364, info=0000', messages[0])
        self.assertEqual('IKJ56236I  FILE STEPLIB INVALID, FILENAME RESTRICTED', messages[1])
        rc, results = zos.dynalloc.dynunalloc({"DDNAME":ddname})
        self.assertEqual(0, rc)
     

def test_main():
    support.run_unittest(zos_dynalloc_test_case)


if __name__ == "__main__":
    test_main()

