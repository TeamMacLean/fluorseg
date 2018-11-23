import unittest
from fluorseg import liffile
from fluorseg import methods
import os

class MethodsTest(unittest.TestCase):

    def setUp(self):
        self.result = methods.extract_volumes_for_rois( os.path.join(
            os.getcwd(), "fluorseg", "test", "data")
        )

    def tearDown(self):
        self.result = None

    def test_as_csv(self):
        csv_list = methods.as_csv(self.result)
        self.assertEqual(csv_list[0][0], "lif_file")
        self.assertAlmostEqual(csv_list[1][-1], 371.44318, 5)
        self.assertAlmostEqual(csv_list[-1][-1], 311.14117, 5)

    def test_filled_result(self):
        self.assertEqual(self.result.lif.img_count, 4 )
        self.assertEqual(len(self.result.roi_file_paths), 4)
        self.assertEqual(len(self.result.max_projects_channel_1), 4)
        self.assertEqual(len(self.result.volumes_channel_1), 4)
        self.assertAlmostEqual(self.result.volumes_channel_2[-1][-1], 311.14117, 5)
