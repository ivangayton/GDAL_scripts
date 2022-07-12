#!/usr/bin/python3
# -*- coding: utf-8 -*-

import argparse
import sys, os

def process(infile, input_corners, outfile, crs, comp):
    """
    Constructs and runs a GDAL command to 
    georeference an ODM orthphoto.
    """

    cp = crs_parameters(crs)
    ulx = uly = lrx = lry = 0.0
    with open(input_corners) as f:
        for lineNumber, line in enumerate(f):
            if lineNumber == 0:
                tokens = line.split(' ')
                if len(tokens) == 4:
                    ulx = float(tokens[0]) + \
                        float(cp['east_offset'])
                    lry = float(tokens[1]) + \
                        float(cp['north_offset'])
                    lrx = float(tokens[2]) + \
                        float(cp['east_offset'])
                    uly = float(tokens[3]) + \
                        float(cp['north_offset'])

    epsg = cp['EPSG_ID']

    compress = ''
    if comp:
        compress = (f'-co COMPRESS=JPEG '
                    f'-co PHOTOMETRIC=YCBCR '
                    f'-b 1 -b 2 -b 3 -mask 4 '
                    f'--config GDAL_TIFF_INTERNAL_MASK YES ')

    cmd_str = (f'gdal_translate '
               f'-a_srs {epsg} '
               f'-a_ullr {ulx} {uly} {lrx} {lry} '
               #f'--config GDAL_CACHEMAX {max_memory}% '
               f'--config GDAL_TIFF_INTERNAL_MASK YES '
               f'{compress}'
               f'-co TILED=YES '
               f'-co BIGTIFF=IF_SAFER '
               f'"{infile}" "{outfile}"')
    
    print(f'Trying to create a GeoTIFF with the command:\n\n{cmd_str}\n') 
    os.system(cmd_str)


def crs_parameters(epsg_string):
    """
    Eventually should be able to ingest a Proj string,
    EPSG ID, or any geographical file with a CRS in it.
    Returns the appropriate ID string, as well as
    (for UTM) the false easting and northing (offsets)
    which are required to correct the georeferencing
    coordinates.
    Returns a dictionary. A tuple would
    be simpler, but since different CRSs have different
    types and numbers of keys and values, a dict is
    probably sensible.
    For now shamelessly hard-coded to 
    32736 (UTM zone 36 South with WGS84 datum)
    """
    print(f'\nPretending to produce relevant ' \
          f'CRS data from {epsg_string}\n')
    return{'EPSG_ID': 'EPSG:32736',
           'east_offset': 500000,
           'north_offset': 10000000}

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    # Positional arguments
    p.add_argument("input_tiff",
                   help='GeoTIFF raster to be georeferenced')
    p.add_argument("input_corners",
                   help='Text file defining the corners of the raster')
    p.add_argument("output_tiff",
                   help='Output filename')

    # Flag arguments
    p.add_argument('-crs', '--coordinate_reference_system',
                   help='The coordinate reference system')
    p.add_argument('-c', '--compress', action='store_true',
                   help='Choose to compress using YCbCr jpeg')


    args = p.parse_args()
    
    process(args.input_tiff,
            args.input_corners,
            args.output_tiff,
            args.coordinate_reference_system,
            args.compress)
