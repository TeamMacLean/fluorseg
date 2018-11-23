import unittest
from fluorseg import liffile
import os

class LifFileTest(unittest.TestCase):


    def test_create_lif(self):
        test_lif = os.path.join( os.getcwd(), "fluorseg", "test", "data", "PR2729_frameOrderCombinedScanTypes.lif")
        lif_obj = liffile.LIFFile(test_lif)
        self.assertEqual(lif_obj.path, test_lif)


if __name__ == '__main__':
    unittest.main()
