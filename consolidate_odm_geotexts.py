#!/bin/python3

"""
OpenDroneMap (ODM) input data (aerial photos) often has a 
geo.txt file associated with each directory of photos, 
representing the photo geolocations. 
It can be useful to inspect the locations in a GIS. This 
script grabs all of the geo.txt files from every subdirectory
in a given directory, and compiles them to a single CSV
file suitable for import into QGIS.

The directory structure might look something like this:
>my_flight_data/
  >Mission/
  |>odm_dem/
    -dsm.tif
    -dtm.tif
  >odm_georeferencing/
  |>odm_orthophoto/
    -odm_orthophoto.tif
  >odm_report/
  >
  -geo.txt
  
"""
import sys, os
import csv
import argparse

def get_image_dirs(indir):
    """
    make a list of directories containing images and a 
    geo.txt file. 
    """
    dirlist = []
    for path, dirs, files in os.walk(indir):
        for d in dirs:
            dirlist.append(os.path.join(path, d))
    image_dirs = []
    for d in dirlist:
        geotext = os.path.join(image_dir, 'geo.txt')
        # TODO maybe also check if there are images
        if(os.path.isfile(geotext)):
            odm_dirs.append(d)
    return image_dirs

def consolidate_geotexts(indir):
    image_dirs = get_image_dirs(indir)
    for image_dir in image_dirs:
        original = os.path.join(odm_dir, 'geo.txt')
        basename = os.path.split(odm_dir)[-1]
        



if __name__ == '__main__':
    """
    Consolidates ODM outputs from multiple directories 
    and projects
    """
    
    p = argparse.ArgumentParser()

    p.add_argument("indir",
                   help="Input directory full of ODM image dirs")

    a = p.parse_args()

    r = consolidate_geotexts(a.indir)
