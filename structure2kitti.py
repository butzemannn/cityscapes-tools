#!/usr/bin/env python3

import argparse
import shutil


# TODO: split txt files erstellen (and make them optional)
# TODO: make MMDetection3D ImageSets optional
from utils.csstructure import list_subdirs


def _setup_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert the Cityscapes folder structure to kitti structure.")
    parser.add_argument("vel_source_folder", type=str, help="The cityscapes folder which should be converted.")
    parser.add_argument("gt_folder", type=str)
    parser.add_argument("color_folder", type=str)
    parser.add_argument("dest_folder", type=str, help="Resulting folder.")
    parser.add_argument("--copy", type=bool, default=False, help="Should the operation copy the files.")

    return parser.parse_args()


def create_split(count: int, path: str) -> None:
    # TODO: make parameter
    path = "/media/data/datasets/cityscapes/kitti/ImageSets"
    try:
        train = open(f"{path}/train.txt", 'w+')
        trainval = open(f"{path}/trainval.txt", 'w+')

        for i in range(0, count):
            train.write(f"{i:06}\n")
            trainval.write(f"{i:06}\n")
    finally:
        train.close()
        trainval.close()


def main(vel_folder: str, gt_folder: str, color_folder: str, calilb_folder: str, image_foler: str, dest_folder: str, copy: bool):
    vel_files = list_subdirs(vel_folder)
    # TODO: check if files length is too long for padding
    # TODO: create parent folder if not existing
    create_split(len(vel_files), f"{dest_folder}/ImageSets")
    for i, rel_file_path in enumerate(vel_files):
        vel_source = f"{vel_folder}/{rel_file_path}"
        gt_source = f"{gt_folder}/{rel_file_path[:-12]}gtBbox3d.txt"
        color_source = f"{color_folder}/{rel_file_path[:-12]}color.npy"
        calib_source = f"{calilb_folder}/{rel_file_path[:-12]}camera.json"
        image_source = f"{image_foler}/{rel_file_path[:-12]}leftImg8bit.png"

        # Pad destination file with leading zeros
        vel_dest = f"{dest_folder}/velodyne/{i:06}.bin"
        gt_dest = f"{dest_folder}/label_2/{i:06}.txt"
        color_dest = f"{dest_folder}/color/{i:06}.npy"
        calib_dest = f"{dest_folder}/calib/{i:06}.json"
        image_dest = f"{dest_folder}/image_2/{i:06}.png"

        # either move or copy files depending on parameter
        shutil.copy(vel_source, vel_dest)
        shutil.copy(gt_source, gt_dest)
        shutil.copy(color_source, color_dest)
        shutil.copy(calib_source, calib_dest)
        shutil.copy(image_source, image_dest)
        # copy_function = shutil.copy if copy else shutil.copy2
        # shutil.move(vel_source, vel_dest, copy_function=copy_function)
        # shutil.move(gt_source, gt_dest, copy_function=copy_function)
        # shutil.move(color_source, color_dest, copy_function=copy_function)
        # shutil.move(calib_source, calib_dest, copy_function=copy_function)
        # shutil.move(image_source, image_dest, copy_function=copy_function)


if __name__ == '__main__':
    args = _setup_arguments()
    main(args.vel_source_folder, args.dest_folder, args.copy)

