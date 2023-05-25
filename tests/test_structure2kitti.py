import unittest

from structure2kitti import main


class MyTestCase(unittest.TestCase):

    def test_main(self):
        vel_folder = "/media/data/datasets/cityscapes/velodyne/val/"
        gt_folder = "/media/data/datasets/cityscapes/kitti_gt/val/"
        color_folder = "/media/data/datasets/cityscapes/pccolor/val/"
        calib_folder = "/media/data/datasets/cityscapes/camera/val/"
        image_folder = "/media/data/datasets/cityscapes/leftImg8bit/val/"
        dest_folder = "/media/data/datasets/cityscapes/kitti/validation"
        main(vel_folder, gt_folder, color_folder, calib_folder, image_folder, dest_folder, True)


if __name__ == '__main__':
    unittest.main()
