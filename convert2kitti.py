#!/bin/env python3
# Converts Cityscapes ground truth boxes to kitti format

import argparse
import os
import json

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


def setup_arguments() -> argparse.Namespace:
    """
    Setup arguments
    :return:
    """
    parser = argparse.ArgumentParser(description="Converts Cityscapes ground truth boxes to kitti format.")
    parser.add_argument('source_folder', type=str, help='Source folder containing cityscapes ground truth files.')
    parser.add_argument('dest_folder', type=str,
                        help='Destination folder where newly created ground truth files should be stored.')

    return parser.parse_args()


def generate_calib(source_data: dict):
    pass


def _convert_occulsion(occlusion: float) -> int:
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


def generate_objects(source_data: dict):
    resulting_objects = []
    objects = source_data['objects']
    for object in objects:
        if not object['label'] == 'car':
            # currently only cars tested
            continue
        kitti_gt = [
            'Car',
            object['truncation'],
            _convert_occulsion(object['occlusion']),
            

        ]

        resulting_objects.append(kitti_gt)


def main(source_folder: str, dest_folder: str):
    # TODO: check if file is json
    source_files = os.listdir(source_folder)
    for source_file in source_files:
        with open(f"{source_folder}/{source_file}") as f:
            source_data = json.load(f)
            # generate_calib(source_data)
            generate_objects(source_data)


if __name__ == "__main__":
    args = setup_arguments()
    main(args.source_folder, args.dest_folder)
