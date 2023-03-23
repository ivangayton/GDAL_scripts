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
  >Mission1/
    >flight1/
      geo.txt
      M01_F01_0001.JPG
      M01_F01_0002.JPG
      ...
    >flight2
      geo.txt
      M01_F02_0001.JPG
      M01_F02_0002.JPG
      ...
    ...
  >Mission2/
    ...
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
        geotext = os.path.join(d, 'geo.txt')
        # Also check if there are images, not essential
        if(os.path.isfile(geotext)):
            image_dirs.append(d)
    return image_dirs

def consolidate_geotexts(indir):
    image_dirs = get_image_dirs(indir)
    with open(os.path.join(indir, 'geolocations.csv'), 'w') as locationsfile:
        w = csv.writer(locationsfile)
        header = ['filename', 'x','y','z','omega','phi','kappa',
                  'hacc','vacc','block']
        w.writerow(header)
        for image_dir in image_dirs:
            geotextfile = os.path.join(image_dir, 'geo.txt')
            basename = os.path.split(os.path.split(image_dir)[0])[-1]
            blockname = basename.replace(' ','_')
            geotext = open(geotextfile, 'r')
            locations = geotext.readlines()
            crs = locations.pop(0) # mutates location removing first line
            for location in locations:
                row = location.split()
                row.append(blockname)
                w.writerow(row)
            print(f'adding locations from {blockname}')
        
        



if __name__ == '__main__':
    """
    Consolidates ODM outputs from multiple directories 
    and projects
    """
    
    p = argparse.ArgumentParser()

    p.add_argument("indir",
                   help="Input directory full of ODM image dirs")

    #TODO: implement a parameter to indicate how many directories deep the
    # geo.txt file is from the shallower address.
    p.add_argument("namedir", default = 2,
                   help="number of nesting levels below the geo.txt file"
                   "the name should be taken from")
    
    a = p.parse_args()

    r = consolidate_geotexts(a.indir)
