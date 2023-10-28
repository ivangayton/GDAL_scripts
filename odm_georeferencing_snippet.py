#!/usr/bin/python3
# -*- coding: utf-8 -*-

import argparse
import sys, os

def process(infile, input_corners, outfile,
            crs, eoff, noff, comp, edit):
    """
    Constructs and runs a GDAL command to 
    georeference an ODM orthphoto.
    """

    (ulx, uly, lrx, lry) = get_corners(input_corners,
                                       eoff, noff)
    
    compress = ''
    if comp:
        compress = (f'-co COMPRESS=JPEG '
                    f'-co PHOTOMETRIC=YCBCR '
                    f'-b 1 -b 2 -b 3 -mask 4 '
                    f'--config GDAL_TIFF_INTERNAL_MASK YES ')

    cmd_str = (f'gdal_translate '
               f'-a_srs {crs} '
               f'-a_ullr {ulx} {uly} {lrx} {lry} '
               #f'--config GDAL_CACHEMAX {max_memory}% '
               f'--config GDAL_TIFF_INTERNAL_MASK YES '
               f'{compress}'
               f'-co TILED=YES '
               f'-co BIGTIFF=IF_SAFER '
               f'"{infile}" "{outfile}"')
    
    print(f'Trying to create a GeoTIFF with the ' \
          f'command:\n\n{cmd_str}\n')
    
    os.system(cmd_str)

def get_corners(ic, eoff, noff):
    """
    Parses a text file giving the coordinates of the 
    upper left and lower right corners of a raster.
    Returns a tuple of four coordinates,
    upper left x and y (ulx and uly)
    lower right x and y (lrx and lry)
    Adjusted with the offsets from the CRS 
    (nominally the false easting and northing for UTM).
    """
    ulx = uly = lrx = lry = 0.0
    with open(ic) as f:
        for lineNumber, line in enumerate(f):
            if lineNumber == 0:
                tokens = line.split(' ')
                if len(tokens) == 4:
                    ulx = (0 + #float(tokens[0]) + \
                           float(eoff))
                    lry = (0 + #float(tokens[1]) + \
                           float(noff))
                    lrx = (0 + #float(tokens[2]) + \
                           float(eoff))
                    uly = (0 + #float(tokens[3]) + \
                           float(noff))
    return(ulx, uly, lrx, lry)

def crs_parameters(epsg_string):
    """
    Eventually should be able to ingest a Proj string,
    EPSG ID, or any geographical file with a CRS in it
    and return
    """
    pass

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
    p.add_argument('-eo', '--east_offset', default=0,
                   help='The east offset')
    p.add_argument('-no', '--north_offset', default=0,
                   help='The north offset'),
    p.add_argument('-c', '--compress', action='store_true',
                   help='Choose to compress using YCbCr jpeg')
    p.add_argument('-e', '--edit', action='store_true',
                   help='edit infile instead of creating outfile')

    args = p.parse_args()
    process(args.input_tiff,
            args.input_corners,
            args.output_tiff,
            args.coordinate_reference_system,
            args.east_offset,
            args.north_offset,
            args.compress,
            args.edit)
