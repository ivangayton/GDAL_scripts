#! /usr/bin/python3
"""
Extracts the GPS locations from EXIF data from a directory full of 
Sensefly Ebee camera images. Not sure if it works with other cameras as it's
currently only set up for the specific numerical format of the EXIF data
the Ebee camera creates (degrees, minutes, and seconds as a Ratio datatype).

Creates a CSV file containing the file basenames, the paths, and the lats and
lons in decimal degree format for all images, suitable for importation into 
QGIS as delimited text.

Expects a single argument: a directory. Recursively traverses all
subdirectories, so it'll give you a CSV with info from all .jpg images in the
folder and all subfolders. The CSV file will be in the same parent folder as
the input directory, and will have the same name with a .csv extension. 

Requires the exifread library, available on pip (pip install exifread). 
Might be sensible to rewrite using PIL (or pillow) library to make it a more
common dependency. Not urgent.
"""

import sys, os
import csv
import exifread

def scandir(dir):
    """Walk recursively through a directory and return a list of all files in it"""
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
    with open(infile, 'rb') as f:
        tags = exifread.process_file(f)
        lattag = tags.get('GPS GPSLatitude')
        latref = tags.get('GPS GPSLatitudeRef')
        lontag = tags.get('GPS GPSLongitude')
        lonref = tags.get('GPS GPSLongitudeRef')

        lat = exif_GPS_to_decimal_degrees(lattag)
        lon = exif_GPS_to_decimal_degrees(lontag)
        if latref.values == 'S':
            lat = -lat
        if lonref.values == 'W':
            lon = -lon
        return(lat, lon)

def create_geotag_list(indir):
    """Create a CSV file with a list of photos and their lat & long"""
    outfile = indir + '.csv'
    image_files = scandir(indir)
    writer = csv.writer(open(outfile, 'w'), delimiter = ';')
    writer.writerow(['file', 'path', 'lat', 'lon'])
    
    for image_file in image_files:
        (image_path, image_ext) = os.path.splitext(image_file)
        image_filename = os.path.basename(image_file)
        if(image_ext == '.JPG' or image_ext == '.jpg'):
            coords = extract_location(image_file)
            writer.writerow([image_filename, image_file, coords[0], coords[1]]) 
    
    
if __name__ == "__main__":
    """Expects a directory as the sole argument"""
    create_geotag_list(sys.argv[1])
