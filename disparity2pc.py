#!/usr/env python3

import argparse

import numpy
import numpy as np
import cv2
import os
import json
from alive_progress import alive_bar
from typing import Tuple

from utils.csstructure import list_subdirs, create_parent_dirs


class Camera:
    def __init__(self, parameters: dict):
        """
        Initialize Camera object from cityscapes data

        :param parameters: Dict in the cityscapes camera parameters form
        """
        self.b = parameters["extrinsic"]["baseline"]
        self.v_0 = parameters["intrinsic"]["v0"]
        self.u_0 = parameters["intrinsic"]["u0"]
        self.f_x = parameters["intrinsic"]["fx"]
        self.f_y = parameters["intrinsic"]["fy"]


def _setup_arguments() -> argparse.Namespace:
    """
    Setup arguments for command line interface application

    :return: Arguments parsed by the library
    """
    parser = argparse.ArgumentParser(description="Convert Cityscapes disparity to point clouds.")
    parser.add_argument("disp_folder", type=str, help="Source folder containing disparity maps.")
    parser.add_argument("camera_folder", type=str, help="Camera parameter folder.")
    parser.add_argument("dest_folder", type=str,
                        help="Destination folder in which the resulting point clouds will be stored. "
                             "Will be stored in csv format.jk")
    parser.add_argument("--color", type=str, help="Optional parameter to specify point cloud color information.")
    parser.add_argument("--images", type=str, help="The left camera image folder which contains the png input images.")

    return parser.parse_args()


def load_files(disp_file: str, calib_file: str) -> Tuple[np.ndarray, Camera]:
    """
    Load cityscapes and process cityscapes files. Also generate Camera object from calibration file.

    :param disp_file: String giving the disparity file location
    :param calib_file: String giving the calibration file location
    :return: [disparity, camera], an array containing
    """
    # Disparity has to be transformed according to https://github.com/mcordts/cityscapesScripts
    # see https://github.com/mcordts/cityscapesScripts/issues/55
    disparity = cv2.imread(disp_file, cv2.IMREAD_UNCHANGED).astype(np.float32)
    disparity[disparity > 0] = (disparity[disparity > 0] - 1) / 256
    # Swap axes since opencv coordinates do not work with image coordinates
    disparity = np.swapaxes(disparity, 0, 1)

    with open(calib_file) as f:
        calib = json.load(f)

    camera = Camera(calib)
    return disparity, camera


# TODO: Decide format (csv or bin)
def store_file(data: np.ndarray, file: str) -> None:
    """Save in .bin format"""
    data = data.reshape([data.shape[0] * data.shape[1]])
    data = data.astype("float32")

    # create directories
    create_parent_dirs(file)
    data.tofile(file)


def convert_file(disparity: np.ndarray, camera: Camera) -> tuple:
    """
    Transformation reference:
    'Pseudo-LiDAR from Visual Depth Estimation Bridging the Gap in 3D Object Detection for Autonomous Driving'
    https://arxiv.org/pdf/1812.07179.pdf

    :param disparity:
    :param camera:
    :return:
    """
    lx, ly = disparity.shape
    u = np.expand_dims(np.arange(lx), axis=1)
    v = np.expand_dims(np.arange(ly), axis=0)
    u = np.broadcast_to(u, (lx, ly))
    v = np.broadcast_to(v, (lx, ly))

    # Depth D
    D = np.reciprocal(disparity) * camera.f_x * camera.b

    # 3 dimensional coordinates and reflectance
    x = (1/camera.f_x) * (np.multiply(D, u - camera.u_0))
    y = (1/camera.f_y) * (np.multiply(D, v - camera.v_0))
    z = D
    r = np.ones(x.shape)

    # Transform axis
    x, y, z = z, -x, -y

    point_cloud = np.stack((x, y, z, r), axis=-1)
    point_cloud = np.reshape(point_cloud, (-1, point_cloud.shape[-1]))
    # filter inf values
    mask = np.all(np.isfinite(point_cloud), axis=1)
    return point_cloud[mask], mask


def generate_color(image_file: str, color_file: str, mask: np.ndarray):
    image = cv2.imread(image_file).astype(np.float32)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    # Swap axes since opencv coordinates do not work with image coordinates
    image = np.swapaxes(image, 0, 1)
    image = np.reshape(image, (-1, image.shape[-1]))
    image = image[mask] / 256

    create_parent_dirs(color_file)
    #numpy.save(color_file, image)


def main(disp_folder: str, calib_folder: str, dest_folder: str, image_folder: str = None, color_folder: str = None) -> None:
    """

    :param color_folder:
    :param disp_folder:
    :param calib_folder:
    :param dest_folder:
    :return:
    """
    disp_files = list_subdirs(disp_folder)
    #with alive_bar(len(disp_files)) as bar:
    for disp_rel_path in disp_files:
        disp_file = f"{disp_folder}/{disp_rel_path}"
        calib_file = f"{calib_folder}/{disp_rel_path[:-13]}camera.json"
        dest_file = f"{dest_folder}/{disp_rel_path[:-13]}velodyne.bin"
        image_file = f"{image_folder}/{disp_rel_path[:-13]}leftImg8bit.png"
        color_file = f"{color_folder}/{disp_rel_path[:-13]}color.npy"

        disparity, camera = load_files(disp_file, calib_file)
        point_cloud, mask = convert_file(disparity, camera)
        #store_file(point_cloud, dest_file)
        if color_folder:
            generate_color(image_file, color_file, mask)

            # Advance bar
            #bar()


if __name__ == '__main__':
    args = _setup_arguments()
    main(args.disp_folder, args.camera_folder, args.dest_folder, image_folder=args.images, color_folder=args.color)
