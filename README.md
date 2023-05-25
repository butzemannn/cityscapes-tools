# Cityscapes-Tools - Useful dataset helpers
Tools for working with cityscapes dataset. Includes tools like ground truth, disparity and structure conversion.

# Included scripts

## disparity2pc.py

Converts the cityscapes disparity file to point cloud data in binary format, which is similar to the format kitti is using. Also provides the ability to export color information as numpy files,
which can then be used in a point cloud viewer.

### Parameters
```
usage: disparity2pc.py [-h] [--color COLOR] [--images IMAGES] disp_folder camera_folder dest_folder

Convert Cityscapes disparity to point clouds.

positional arguments:
  disp_folder      Source folder containing disparity maps.
  camera_folder    Camera parameter folder.
  dest_folder      Destination folder in which the resulting point clouds will be stored. Will be stored in csv format.jk

optional arguments:
  -h, --help       show this help message and exit
  --color COLOR    Optional parameter to specify point cloud color information.
  --images IMAGES  The left camera image folder which contains the png input images.
```

## gt2kitti.py

Convert Cityscapes ground truth files to kitti format. This comes in handy if cityscapes ground truth data is not supported, but kitti is. Please keep in mind that some ground truth
data is lost during this conversion process. This includes for exmaple the exact 3 dimensional rotation information as well as a more detailed object categorisation.
For this conversion process, the official cityscapes-tool library is used and required.

### Parameters

```
usage: gt2kitti.py [-h] source_folder dest_folder

Converts Cityscapes ground truth boxes to kitti format.

positional arguments:
  source_folder  Source folder containing cityscapes ground truth files.
  dest_folder    Destination folder where newly created ground truth files should be stored.

optional arguments:
  -h, --help     show this help message and exit
```

## structure2kitti.py

A script which helps to convert the cityscapes to kitti folder structure. This is helpful if the library, which is used, does not support cityscapes as a dataset.
Will most likely be used in combination with the `gt2kitti.py` script, which converts the cityscapes ground truth to kitti format.

### Usage




### Parameters


```
usage: structure2kitti.py [-h] [--copy COPY] vel_source_folder gt_folder color_folder dest_folder

Convert the Cityscapes folder structure to kitti structure.

positional arguments:
  vel_source_folder  The cityscapes folder which should be converted.
  gt_folder	     Folder containing the ground truths
  color_folder	     Folder containing the numpy color information. Useful if displayed with a point cloud viewer.
  dest_folder        Destination folder.

optional arguments:
  -h, --help         show this help message and exit
  --copy COPY        Should the operation copy the files.
```


