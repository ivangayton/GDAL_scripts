#!/bin/python3

"""
OpenDroneMap (ODM) creates a number of outputs for a given set of input photos.
The directory structure looks like this:
>my_flight_area/
  >entwine_pointcloud/
  |>odm_dem/
    -dsm.tif
    -dtm.tif
  >odm_georeferencing/
  |>odm_orthophoto/
    -odm_orthophoto.tif
  >odm_report/
  >odm_texturing/
  -cameras.json
  -images.json
  -log.json
  -task_output.txt

If you have multiple datasets in the same area and want to inspect the orthphotos and/or Digital Elevation Models (DEMs) all together, it's a hassle to open them in a GIS because they're in separate directories, nested two deep, and the filenames are all the same (making it difficult to know which is which in the table of contents of the GIS). 

This script iterates through a directory full of ODM output directories, grabs the orthophotos (and DEMs if that option is selected), copies them into a single directory within the working dir, and renames the files for for their parent directory's parent (presumably a unique identifier for that project).

So you should get a directory looking like:

|>My_ODM_outputs
  |>orthophotos
    -Mission_01_flight_01.tif
    -Mission_02_flight_02.tif
  
"""
import sys, os
import shutil
import argparse

def get_odm_dirs(indir):
    """make a list of directories containing odm_orthohphoto subdirectories"""
    dirlist = []
    for path, dirs, files in os.walk(indir):
        for d in dirs:
            dirlist.append(os.path.join(path, d))
    odm_dirs = []
    for d in dirlist:
        ortho_dir = os.path.join(d, 'odm_orthophoto')
        ortho_file = os.path.join(ortho_dir, 'odm_orthophoto.tif')
        if(os.path.isfile(ortho_file)):
            odm_dirs.append(d)
    return odm_dirs

def consolidate_orthos(indir):
    odm_dirs = get_odm_dirs(indir)
    orthos_new_dir = os.path.join(indir, '0_orthophotos')
    if not os.path.exists(orthos_new_dir):
        print(f'\nCreating {orthos_new_dir}')
        os.makedirs(orthos_new_dir)
    for odm_dir in odm_dirs:
        original = os.path.join(odm_dir, 'odm_orthophoto', 'odm_orthophoto.tif')
        basename = os.path.split(odm_dir)[-1]
        # ditch the "-all" at the end of ODM output dir names
        newfilename = f'{basename}.tif'.replace('-all.tif','.tif')
        copy = os.path.join(orthos_new_dir, newfilename)
        print(f'Copying {original} to {copy}')
        shutil.copyfile(original, copy)
    


if __name__ == '__main__':
    """Consolidates ODM outputs from multiple directories and projects"""
    p = argparse.ArgumentParser()

    p.add_argument("indir",
                   help="Input directory full of ODM output directories")
    p.add_argument("-dem", "--digital_elevation_model", action="store_true",
                   help="grabs the dsm and dtm (if present) as well as orthos")

    a = p.parse_args()

    r = consolidate_orthos(a.indir)
