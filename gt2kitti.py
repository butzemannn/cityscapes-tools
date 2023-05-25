#!/usr/env python3
# Converts Cityscapes ground truth boxes to kitti format

import argparse
import os
import json
import quaternion
import sympy
import csv
import math
import numpy as np
from alive_progress import alive_bar
from scipy.spatial.transform import Rotation

from lib.cityscapesScripts.cityscapesscripts.helpers.annotation import CsBbox3d
from lib.cityscapesScripts.cityscapesscripts.helpers.box3dImageTransform import (
    Camera,
    Box3dImageTransform,
    CRS_S,
    CRS_V,
)
from utils.csstructure import list_subdirs, create_parent_dirs

"""
Kitti gt format:

    #Values    Name      Description
----------------------------------------------------------------------------
   1    type         Describes the type of object: 'Car', 'Van', 'Truck',
                     'Pedestrian', 'Person_sitting', 'Cyclist', 'Tram',
                     'Misc' or 'DontCare'
   1    truncated    Float from 0 (non-truncated) to 1 (truncated), where
                     truncated refers to the object leaving image boundaries
   1    occluded     Integer (0,1,2,3) indicating occlusion state:
                     0 = fully visible, 1 = partly occluded
                     2 = largely occluded, 3 = unknown
   1    alpha        Observation angle of object, ranging [-pi..pi]
   4    bbox         2D bounding box of object in the image (0-based index):
                     contains left, top, right, bottom pixel coordinates
   3    dimensions   3D object dimensions: height, width, length (in meters)
   3    location     3D object location x,y,z in camera coordinates (in meters)
   1    rotation_y   Rotation ry around Y-axis in camera coordinates [-pi..pi]
   1    score        Only for results: Float, indicating confidence in
                     detection, needed for p/r curves, higher is better.
"""


def _setup_arguments() -> argparse.Namespace:
    """
    Setup arguments for command line interface usage. These include
        source_folder: Folder which contains the cityscapes ground truth files, which should be converted to kitti format.
        dest_folder: The destination folder, where the newly created ground truth files should be saved.

    The resulting folder structure will be the same as the cityscapes structure. For a conversion please refer to the structure2kitti.py file.

    :return: The parsed arguments from argument parser object.
    """
    parser = argparse.ArgumentParser(description="Converts Cityscapes ground truth boxes to kitti format.")
    parser.add_argument('source_folder', type=str, help='Source folder containing cityscapes ground truth files.')
    parser.add_argument('dest_folder', type=str,
                        help='Destination folder where newly created ground truth files should be stored.')

    return parser.parse_args()


def _setup_image_transform(source_data: dict) -> Box3dImageTransform:
    """
    Setup the image transformation according to
    https://github.com/mcordts/cityscapesScripts/blob/master/docs/Box3DImageTransform.ipynb
    """
    camera = Camera(fx=source_data['sensor']['fx'],
                    fy=source_data['sensor']['fy'],
                    u0=source_data['sensor']['u0'],
                    v0=source_data['sensor']['v0'],
                    sensor_T_ISO_8855=source_data['sensor']['sensor_T_ISO_8855'])

    box3d_annotation = Box3dImageTransform(camera=camera)

    return box3d_annotation


def _transform_box(box_data: dict, box3d_annotation: Box3dImageTransform) -> tuple:
    """
    Transform box with cityscapes toolbox. Has to be transformed to coordinate system CRS_S. Furthermore, the angle 
    has to be converted from quarternion to euler representation. Therefore all three angles have to be regarded, 
    which then avoids problems with flipped boxes.

    :param box_data: A single object's bounding box
    :return:[size_v, center_v, rotation_v] in CRS_S coordinate system.
    """

    obj = CsBbox3d()
    obj.fromJsonText(box_data)
    box3d_annotation.initialize_box_from_annotation(obj, coordinate_system=CRS_V)
    size_v, center_v, rotation_v = box3d_annotation.get_parameters(coordinate_system=CRS_S)

    # angle generation
    r = Rotation.from_quat(rotation_v.elements)
    vector = np.array([0, 0, 1])
    vector = r.apply(vector)
    # project onto plane
    vector[1] = 0
    angle = math.acos(vector[2] / np.linalg.norm(vector))
    if vector[0] > 0:
        # If x component of vector is positive, the angle has to be negated
        angle = -angle

    rotation_v_euler = r.as_euler("xyz", degrees=False)

    return size_v, center_v, angle


def _calculate_alpha(center: list, angle: float) -> float:
    """Returns the observation angle alpha of the bounding box center"""
    x, y, z = center

    return angle + float(sympy.simplify(sympy.atan(x/z)))


def _convert_occlusion(occlusion: float) -> int:
    """
     Converts cityscapes occlusion (float between 0.0 and 1.0) into Kitti format (0, 1, 2 or 3).

     :param occlusion:  Cityscapes occlusion value
     :return: Kitti occlusion format (0, 1, 2, or 3)
     """

    if occlusion == 0.0:
        # fully visible
        return 0
    elif 0.0 < occlusion < 0.5:
        # partly occluded
        return 1
    elif 0.5 <= occlusion <= 1:
        # largely occluded
        return 2
    else:
        # occlusion unknown
        return 3


def generate_objects(source_data: dict) -> list:
    """
    Generates a list of objects in kitti format, which can be then saved to a file
    :param source_data: Data in json format comming from cityscapes dataset
    :return: A list containing all objects in kitti format
    """
    resulting_objects = []
    objects = source_data['objects']
    box3d_annotation = _setup_image_transform(source_data)
    for item in objects:
        if 'car' not in str.lower(item['label']):
            # currently only cars tested
            continue

        size, center, angle = _transform_box(item, box3d_annotation)
        coords_2d = item['2d']['amodal']
        kitti_gt = [
            'Car',
            item['truncation'],
            _convert_occlusion(item['occlusion']),
            _calculate_alpha(center, angle),
            coords_2d[0], coords_2d[1], coords_2d[2], coords_2d[3],
            size[2], size[0], size[1],
            center[0], center[1]+0.5*size[2], center[2],
            angle,
        ]
        resulting_objects.append(kitti_gt)

    return resulting_objects


def save_as_kitti_gt(file_name, objects: list) -> None:
    """
    Save to file with kitti gt format

    :param file_name: The file name. Will be created if not existing.
    :param objects: A list of objects [[obj1..][obj2..]..]
    :return: None
    """
    create_parent_dirs(file_name)
    with open(file_name, 'w+') as f:
        writer = csv.writer(f, delimiter=' ')
        writer.writerows(objects)


def main(source_folder: str, dest_folder: str):
    """
    Execute the main function. Iterate over source folder and load json data. Execute the corresponding program functions.

    :param source_folder: String containing the source folder location
    :param dest_folder: String containing the destination folder, where resulting gt boxes will be stored
    """

    source_files = list_subdirs(source_folder)
    with alive_bar(len(source_files)) as bar:
        for source_file in source_files:
            with open(f"{source_folder}/{source_file}") as f:
                try:
                    source_data = json.load(f)
                except ValueError:
                    print("Error while loading json file.")

                # generate_calib(source_data)
                objects = generate_objects(source_data)
                save_as_kitti_gt(f"{dest_folder}/{source_file[:-5]}.txt", objects)
                bar()


if __name__ == "__main__":
    args = _setup_arguments()
    main(args.source_folder, args.dest_folder)
