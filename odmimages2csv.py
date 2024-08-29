#!/usr/bin/python3
"""
Takes the images.json output from OpenDroneMap and writes a CSV file suitable
for easy viewing as a 3D point layer in QGIS.

NOT a general tool. Unlikely to produce useful results for an arbitrary json
file, but quite likely to work well for the images.json file produced by ODM.

Takes two positional arguments:
1. Input file, /path/to/images.json file from an OpenDroneMap run
2. Output file, /path/to/images.csv would be a sensible choice
"""

import sys
import json
import csv

def odmimages2csv(infile):
    """
    Parse flat json and return list of lists suitable for writing as csv.
    Assumes all json objects have the same keys. Uses the keys of the first
    json object as a header row, then populates the remaining rows with the
    values from those keys for all objects.
    """
    f = open(infile)
    images = json.load(f)
    headers = list(images[0].keys())
    rows = []
    rows.append(headers)
    for image in images:
        row = []
        for header in headers:
            item = image[header]
            row.append(item)
        rows.append(row)
    return rows
    
if __name__ == '__main__':
    """
    Takes two positional arguments:
    1. Input file, /path/to/images.json file from an OpenDroneMap run
    2. Output file, /path/to/images.csv would be a sensible choice
    """
    infile = sys.argv[1]
    outfile = sys.argv[2]
    imagepoints = odmimages2csv(infile)
    with open(outfile, 'w') as of:
        w = csv.writer(of)
        w.writerows(imagepoints)

