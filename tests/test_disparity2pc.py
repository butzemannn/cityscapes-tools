from unittest import TestCase

from disparity2pc import main


class TestMain(TestCase):
    def test_main(self):
        disp_folder = "/media/data/datasets/cityscapes/disparity/"
        camera_folder = "/media/data/datasets/cityscapes/camera/"
        dest_folder = "/media/data/datasets/cityscapes/velodyne/"
        images_folder = "/media/data/datasets/cityscapes/leftImg8bit/"
        color_folder = "/media/data/datasets/cityscapes/pccolor/"
        main(disp_folder, camera_folder, dest_folder=dest_folder, image_folder=images_folder, color_folder=color_folder)
        self.fail()
