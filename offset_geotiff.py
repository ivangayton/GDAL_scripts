#!/usr/bin/python3
# -*- coding: utf-8 -*-

import argparse
import sys, os
from osgeo import gdal, ogr, osr

def shift(infile, xoffset, yoffset):
    """
    Overwrite the GeoTransform of a GeoTIFF to translate it to a new position.
    No rotation or scaling. 
    """
    ds = gdal.Open(infile, gdal.GA_Update)
    gt = ds.GetGeoTransform()
    newgt = (gt[0] + xoffset,
             gt[1],
             gt[2],
             gt[3] + yoffset,
             gt[4],
             gt[5])
    ds.SetGeoTransform(newgt)
    ds = None
    print(f'Old GeoTransform: {gt}'
          f'\nOffset: {xoffset}, {yoffset}'
          f'\nNew Geotransform: {newgt}')
    
def get_corners(infile):
    """
    Grab the corners of a GeoTIFF.
    """
    ds = gdal.Open(infile)
    gt = ds.GetGeoTransform()
    ul = (gt[0], gt[3])
    width = ds.RasterXSize
    height = ds.RasterYSize
    lr = gdal.ApplyGeoTransform(gt, float(width), float(height))

    # ulx uly lrx lry
    return(ul[0], ul[1], lr[0], lr[1])

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    # Positional arguments

    # Flag arguments
    p.add_argument('-i', '--input',
                   help='GeoTIFF raster to be georeferenced')
    p.add_argument('-crs', '--coordinate_reference_system',
                   help='The coordinate reference system')
    p.add_argument('-x', '--x_offset', type=float,
                   help='The x offset')
    p.add_argument('-y', '--y_offset', type=float,
                   help='The y offset'),

    args = p.parse_args()

    shift = shift(args.input, args.x_offset, args.y_offset)
