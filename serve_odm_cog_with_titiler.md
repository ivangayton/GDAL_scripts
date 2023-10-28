# Serve a Cloud-Optimized GeoTIFF from OpenDroneMap using Titiler

So you have a Cloud-Optimized GeoTIFF (COG), perhaps from OpenDroneMap (ODM), and you want to serve it to the world as a Tile Mill Server (TMS) link from a cloud or local server?

You've come to the right place.

Here's a quick recipe using [Titiler](https://developmentseed.org/titiler/), a fantastic Free Software utility built by [DevelopmentSeed](https://developmentseed.org/)for doing exactly that.

# Make sure you have a valid COG
## Check the one you have
[This utility by Even Roault](https://github.com/OSGeo/gdal/blob/master/swig/python/gdal-utils/osgeo_utils/samples/validate_cloud_optimized_geotiff.py) will tell you if your file is a valid COG. Assuming you have `gdal-bin` installed, copying this Python file and running it `python3 validate_cloud_optimized_geotiff.py INFILE.tif` should tell you.

## But you might want to compress it nicely anyway.
In which case you can use one of the recipes from [this utility](compress_tif_using_jpeg_ycbcr.sh). The line I most often use is

```
gdal_translate -co COMPRESS=JPEG -co PHOTOMETRIC=YCBCR -co TILED=YES -b 1 -b 2 -b 3 -mask 4 --config GDAL_TIFF_INTERNAL_MASK YES -co BIGTIFF=IF_SAFER INFILE.tif OUTFILE.tif
```
followed by
```
gdaladdo -r average --config BIGTIFF_OVERVIEW=IF_SAFER INFILE.tif 2 4 8 16 32 64 128 256 512 1024
```

# Install titiler
Use pip

