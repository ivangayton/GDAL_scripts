#!/bin/bash

# These snippets will create a very space and performance-efficient
# GeoTiff raster image file from almost any type of raster that GDAL can parse.

# Based on advice from:
# http://blog.cleverelephant.ca/2015/02/geotiff-compression-for-dummies.html
# and information from:
# https://www.gdal.org/gdal_translate.html

# If your input file has 4 bands, you'll need to specify the three bands
# and the mask (in this case the Alpha) band. Also enable internal mask.
# in order to use YCBCR colorspace
gdal_translate -co COMPRESS=JPEG -co PHOTOMETRIC=YCBCR -co TILED=YES -b 1 -b 2 -b 3 -mask 4 --config GDAL_TIFF_INTERNAL_MASK YES INFILE.tif OUTFILE.tif

# If your input file only has 3 bands, this is all you need:
gdal_translate -co COMPRESS=JPEG -co PHOTOMETRIC=YCBCR -co TILED=YES INFILE.tif OUTFILE.tif

# The resulting file will be slow to load at low zoom levels due to the
# lack of pyramids (overviews)
# Note: it might seem insane to go all the way to 1024, but the only real
# disadvantage of overviews are file size, and anything beyond the first
# few levels (2 and 4) barely contributes to filesize at all! There not much
# reason to hesitate.
gdaladdo -r average INFILE.tif 2 4 8 16 32 64 128 256 512 1024

# If you're working with large rasters, there's always the risk of overflowing the GeoTiff format limit. If you're worried about this, you can specify the use of BigTIFF format that allow substantially larger file/area sizes (disadvantage: some older programs might not be able to read them). So like this:

gdal_translate -co COMPRESS=JPEG -co PHOTOMETRIC=YCBCR -co TILED=YES -b 1 -b 2 -b 3 -mask 4 --config GDAL_TIFF_INTERNAL_MASK YES --co BIGTIFF=IF_SAFER INFILE.tif OUTFILE.tif

# and

gdaladdo -r average --config BIGTIFF_OVERVIEW=IF_SAFER INFILE.tif 2 4 8 16 32 64 128 256 512 1024
