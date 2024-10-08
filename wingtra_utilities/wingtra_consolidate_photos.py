#! /usr/bin/python3
"""

"""

import sys, os
import shutil

def scandir(dir):
    """Walk recursively through a directory and 
    return a list of all files in it"""
    filelist = []
    for path, dirs, files in os.walk(dir):
        for f in files:
            filelist.append(f)
    return filelist

def is_wingtra_dir(indir):
    """Checks if a directory has an IMAGES subdirectory
    with at least one JPG image file in it,
    and a DATA subdirectory containing at least one json file
    which would be consistent with a Wingtra data directory.
    """
    
    dp = os.path.join(indir, 'DATA')
    ip = os.path.join(indir, 'IMAGES')
    if os.path.exists(dp) and os.path.exists(ip):
        all_data_files = os.listdir(dp)
        flight_log_file = [f for f in all_data_files if
                           os.path.splitext(f)[1].lower() == '.json']
        all_image_files = os.listdir(ip)
        imagefilelist = [f for f in all_image_files if
                         os.path.splitext(f)[1].lower() == '.jpg']
        if imagefilelist and flight_log_file:
            return True
        else:
            return False
    else:
        return False
        
def get_wingtra_dirs(indir):
    """Find directories containing DATA and IMAGES subdirs"""
    dirlist = []
    for path, dirs, files in os.walk(indir):
        for d in dirs:
            dirlist.append(os.path.join(path, d))
    wingtra_dirs = []
    for d in dirlist:
        if is_wingtra_dir(d):
            wingtra_dirs.append(d)
    return wingtra_dirs

def consolidate(indir):
    """
    Side effects: writes outfiles

    Creates a single directory full of images and a geo.txt file
    ready for upload to OpenDroneMap.

    """
    # Get a list of Wingtra flight directories in the input dir
    wingtra_dirs = get_wingtra_dirs(indir)
    print(f'\nFound: \n{wingtra_dirs} \nin the input directory')
    imagedir = os.path.join(indir, 'IMAGES')
    if not os.path.exists(imagedir):
        print(f'\nCreating {imagedir}')
        os.makedirs(imagedir)
    geotext = open(os.path.join(imagedir, 'geo.txt'),'w')
    geotext.write('EPSG:4326\n') # I know, I know, bad
    for wdir in wingtra_dirs:
        local_image_dir = os.path.join(wdir, 'IMAGES')
        all_files = os.listdir(local_image_dir)
        images = [x for x in all_files if
                  os.path.splitext(x)[1].lower() == '.jpg']
        for image in images:
            source = os.path.join(local_image_dir, image)
            destination = os.path.join(imagedir, image)
            shutil.copy(source, destination)
        ingeotextfile = os.path.join(wdir, 'IMAGES', 'geo.txt')
        try:
            ingeotext = open(ingeotextfile)
            ingeotextlines = ingeotext.readlines()
            geotext.writelines(ingeotextlines[1:])
        except Exception as e:
            print(e)
            
if __name__ == "__main__":
    """
    Consolidates multiple directories of flight data from a Wingtra
    drone, and associated OpenDroneMap-style geo.txt files, into
    a single directory for upload to ODM.

    Expects a directory full of sub directories, each with three 
    subdirectories containing an Images directory filled with
    a bunch of sequentially named jpg images, and a DATA directory 
    with a JSON file giving with the locations of the photos taken 
    by the Wingtra (this seems to be Wingtra's default format), and 
    a .txt file generated by wingtra_geotag_photos.py for ODM. 
    Like so:

    -MyMission
      -MyFlight01
        -DATA
          MyFlight01.json
          MyFlight01 WingtraOne.sbf
          MyFlight01.csv
          MyFlight01.txt
        -FLIGHT RECORD
          MyFlight01.ulg
        -IMAGES
          MyFlight02_01_00002.JPG
          MyFlight02_01_00003.JPG
      -MyFlight 02    
        ...

    """
    indir = sys.argv[1]
    print(f'Attempting to consolidate files in {indir}')
    consolidate(indir)
