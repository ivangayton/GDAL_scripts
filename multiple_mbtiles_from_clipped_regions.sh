#!/bin/bash

# Create a set of rasters clipped by a set of shapefiles
# (useful for creating individual MBTile sets for many areas,
# for example in Dar es Salaam we wanted one MBTile set
# for each of 200 sub-wards)

# Keep in mind that this is a batch process (and uses multiple threads)
# and can therefore exceed the memory of the computer and crash. The structure:
#
# for i in *; do
#     some_command -w some_arguments &
# done
# wait
#
# Creates multiple background jobs (because of the &) and waits for all to
# finish before continuing to the next job. This makes efficient use of
# multiple cores and RAM, but can take too much RAM and crash.
# We break our jobs into no more than 10 per folder; your mileage may vary.

# Note that there are two inputs: a folder full of shapefiles and a single
# raster file. In this example, we use a virtual raster comprising multiple
# GeoTiff files, which avoids the problem of blank areas when a given polygon
# overlaps multiple GeoTIFFs).

cd folder_full_of_shapefiles/
for i in *.shp; do
    echo $i
    gdalwarp -cutline $i -crop_to_cutline '/path/to/raster.vrt' $i.tif &
done
wait

for i in *.tif; do
    echo $i
    gdal_translate $i $i.mbtiles -of MBTILES -co TILE_FORMAT=JPEG &
done
wait

for i in *.mbtiles; do
    echo $i
    gdaladdo -r average $i 2 4 8 16 32 64 128 256 512 1024 &
done
wait
cd ../
