#!/usr/env python3

import os


def _list_subdirs(folder: str, rel_path: str = "") -> list:
    """

    :param folder:
    :param rel_path:
    :return:
    """
    files_list = os.listdir(f"{folder}/{rel_path}")
    all_files = []
    for entry in files_list:
        entry_rel_path = os.path.join(rel_path, entry)
        entry_abs_path = f"{folder}/{entry_rel_path}"
        if os.path.isdir(entry_abs_path):
            all_files = all_files + _list_subdirs(folder, entry_rel_path)
        else:
            all_files.append(entry_rel_path)

    return all_files


def list_subdirs(folder: str) -> list:
    """

    :param folder:
    :return:
    """
    return _list_subdirs(folder)


def create_parent_dirs(file_name: str) -> None:
    index = file_name.rfind('/')
    dir_path = file_name[:index + 1]
    os.makedirs(dir_path, exist_ok=True)
