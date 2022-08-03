from unittest import TestCase

from testdata import test_data
from convert2kitti import generate_objects

class TestConvert2Kitti(TestCase):
    def test_main(self):
        self.fail()

    def test_generate_objects(self):
        generate_objects(test_data)
