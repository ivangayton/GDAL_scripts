#! /usr/bin/python3
"""
Extracts the GPS locations from EXIF data from a directory full of 
drone camera images. Not sure if it works with other cameras as it's
currently only set up for the specific numerical format of the EXIF data
that DJI and Sensefly drones create (degrees, minutes, and seconds as a
Ratio datatype).

Creates a CSV file containing the file basenames, 
the paths, and the lats and lons in decimal degree 
format for all images, suitable for importation 
into QGIS as delimited text.

Expects a single argument: a directory. Recursively traverses all
subdirectories, so it'll give you a CSV with info from all .jpg images in the
folder and all subfolders. The CSV file will be in the same parent folder as
the input directory, and will have the same name with a .csv extension. 

Requires the exifread library, available on pip 
(pip3 install exifread). 
Might be sensible to rewrite using PIL (or pillow) 
library to make it a more common dependency. Not urgent.
"""

import sys, os
import csv
import exiftool

def scandir(dir):
    """
    Walk recursively through a directory and return a list 
    of all files in it and its subdirectories.
    """
    filelist = []
    for path, dirs, files in os.walk(dir):
        for f in files:
            filelist.append(os.path.join(path, f))
    return filelist

def exif_GPS_to_decimal_degrees(intag):
    """
    Spit out a decimal degree lat or long.
    Expects an exifread tag full of exifread.utils.Ratio types
    """
    d = float(intag.values[0].num) / float(intag.values[0].den)
    m = float(intag.values[1].num) / float(intag.values[1].den)
    s = float(intag.values[2].num) / float(intag.values[2].den)
    return d + (m / 60.0) + (s / 3600.0)
    
def extract_location(infile):
    """Return the GPS lat and long of a photo from EXIF in decimal degrees"""
    with exiftool.ExifToolHelper() as et:
        try:
            # run exiftool for all tags, should be 1-item list
            md = et.get_metadata(infile)
            # that list item should be a dict of exif and extended exif tags
            tags = md[0]
            return tags
        except Exception as e:
            print(e)
            print('The photo {} failed for some reason'.format(infile))
        
    
def create_geotag_list(indir):
    """Create a CSV file with a list of photos and their lat & long"""
    outfile = indir + '.csv'
    image_files = scandir(indir)
    writer = csv.writer(open(outfile, 'w'), delimiter = ',')

    # Get the keys from the first image and write a header row
    # TODO: if the images are from different machines we may need to
    # add new headers
    keys = extract_location(image_files[0]).keys()
    writer.writerow(keys)
    for image_file in image_files:
        (image_path, image_ext) = os.path.splitext(image_file)
        image_filename = os.path.basename(image_file)
        image_dirname = os.path.dirname(image_file)
        if(image_ext.lower() == '.jpg' or image_ext.lower() == '.dng'):
            tags = extract_location(image_file)
            if(tags):
                vals = []
                for key in keys:
                    val = ""
                    try:
                        val = tags[key]
                    except Exception as e:
                        print(f"Something went wrong")
                    vals.append(val)
                writer.writerow(vals) 
    
    
if __name__ == "__main__":
    """Expects a directory as the sole argument"""
    create_geotag_list(sys.argv[1])
