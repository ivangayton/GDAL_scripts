#! /usr/bin/python3
"""

"""

import sys, os
import csv
import exiftool

def overwrite_fields_in_all_photos(infile: path):
    """ """
    with open(infile) as photolist:
        reader = csv.reader(photolist)
        photos = list(reader)
        header = photos.pop(0)
        fields = header[1:]
        tags = {}

        for phototags in photos:
            # First column is filepath
            tgs = iter(phototags)
            fp = next(tgs)
            for field in fields:
                tags[field] = next(tgs)
            overwrite_fields_in_photo(fp, tags)
                

def overwrite_fields_in_photo(infile: path, fields: dict):
    """Overwrites exif/metadata tags in a photo"""
    with exiftool.ExifToolHelper() as et:
        try:
            md = et.set_tags(infile, tags=fields)
            print(f'{md}: {infile}, {fields}')

        except Exception as e:
            print(e)
            print(f'The photo {infile} failed for some reason')    
    
if __name__ == "__main__":
    """Expects a csv with filepaths as the first column"""
    overwrite_fields_in_all_photos(sys.argv[1])
