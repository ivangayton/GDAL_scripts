#!/bin/bash

# Create a single virtual raster (.vrt) covering the entire area of interest

# Crop the the .vrt to contain only imagery within each individual AOI
for i in *.shp; do
    echo $i
    gdalwarp -cutline $i -crop_to_cutline '/PATH/TO/IMAGE.vrt'  $i.tif &
done

wait

# Translate the resulting cropped GeoTiff files into MBTiles
for i in *.tif; do
    echo $i
    gdal_translate $i $i.mbtiles -of MBTILES -co TILE_FORMAT=JPEG &
done

wait

# Add overview, which in the case of MBTiles means adding lower-zoom tile levels
for i in Imagery/*.mbtiles; do
    echo $i
    gdaladdo -r average $i 2 4 8 16 32 64 128 256 512 1024 &
done

# In case reprojection needed:
# gdalwarp -t_srs EPSG:3857 infile.tif outfile_3857.tif
