# Creating a Digital Terrain Model (DTM) from a photogrammetry point cloud
Tools, notes, and steps for creating a [Digital Terrain Model (DTM)](https://en.wikipedia.org/wiki/Digital_elevation_model) from a [point cloud](https://en.wikipedia.org/wiki/Point_cloud) created by photogrammetry software such as [OpenDroneMap (ODM)](https://www.opendronemap.org/), [Pix4D](https://www.pix4d.com/), [Agisoft](https://www.agisoft.com/), or other.

This process is intended for use with drone photographs in low-income urban settings (it was done out of a need to process drone imagery in Dar es Salaam, Tanzania). 

We have only tested this with ODM, as we are [Free Software](https://en.wikipedia.org/wiki/Free_software) and [open data](https://en.wikipedia.org/wiki/Open_data) advocates and prefer to use tools that respect users' freedom whenever possible. All tools and datasets used here, such as [QGIS](https://qgis.org/), [PDAL](https://pdal.io/), [GDAL](https://gdal.org/), and [OpenStreetMap](https://www.openstreetmap.org/#map=12/24.2011/90.5548) are free (both in the sense of freedom and price). However, there is no reason this process won't work with other kinds of tools and datasets.

## Steps for preparing a Digital Terrain Model
Here we assume you have have one or more point clouds and orthorectified photos, as well as ancillary data such as the polygon extent(s) of the point clouds.

We also assume that you have many features (buildings, vegetation, etc) covering the ground, such that a [Simple Morphological Filter(SMRF)](https://pdal.io/stages/filters.smrf.html) is not sufficient to reliably identify terrain vs feature data. If an SMRF is enough, lucky you; use that and save yourself a lot of time.

### Create and prepare the mask layer
- Digitize visible buildings and high vegetation from the ortho photos. Try to avoid little edges poking out as they cause difficulties later. To be sure, buffer them (for OSM buildings, which are not hyper-precise in most cases, it seems that 1-2m of buffer helps a lot).
- In QGIS, perform the following operations on the mask:
  - Reproject to match the point cloud CRS
  - ```Vector -> Geoprocessing Tools -> Dissolve```
  - ```Vector -> Geometry Tools -> Simplify```. Use a 1m tolerance.
  - Remove all attributes except one labelled "CLS" (which you'll probably have to create using the Field Calculator) and populate it with appropriate classification values, which according to [the LAS spec](http://www.asprs.org/wp-content/uploads/2019/03/LAS_1_4_r14.pdf) are:

| # | Classification type       |
|---|---------------------------|
| 0 | Created, Never Classified |
| 1 | Unclassified              |
| 2 | Ground                    |
| 3 | Low Vegetation            |
| 4 | Medium Vegetation         |
| 5 | High Vegetation           |
| 6 | Building                  |
| 7 | Low Point (Noise)         |

- ```Vector -> Research Tools -> Create Grid``` with a Rectangle (Polygon) type, an extent from your mask layer (you can round that to the nearest 100m to have friendlier coordinates), and ~100m vertical and horizontal spacing (assuming you are using a point cloud from drone photogrammetry and urban buildings; other datasets might require different settings, and in any case I have no idea how optimal these are; I just know they work). Use the same CRS as the mask layer and point cloud. Just create a temporary layer; you'll save it as a file after a few more steps.
- ```Vector -> GeoProcessing Tools -> Clip``` the grid to the _outline_ of your point cloud layer (if you are using ODM, you should have a GeoPackage corresponding to the spatial extent of each point cloud).
- Remove the ID layer (which is now non-sequential because of the clip operation) and save the grid as a GeoPackage (that'll add a new FID column).
  - While you are at it, if your mask layer exceeds the extent of the point cloud, you might as well clip it as well. If you are using OSM data, it may require some cleaning, perhaps using the ```Processing -> Toolbox -> Vector geometry -> Check validity``` tool. Invalid polygons will bork the process further along.
- ```Vector -> Geoprocessing Tools -> Intersection``` to split the mask layer up using the grid (the grid is the overlay layer). Keep the FID from the grid, don't generate a new one for the mask layer (because there will be no tile where there aren't buildings, so the IDs won't match).
- Create a directory called "split_mask" and use ```Vector -> Data Management Tools -> Split Vector Layer``` to save the mask as a single file for each tile. Each one will be a little GeoPackage containing the polygons to classify and clip its corresponding point cloud tile. Make sure these have a field called "CLS" with the appropriate value for each feature type!
- Use ```Vector -> Geoprocessing Tools -> Intersection``` to extract only the grid tiles for each block. Allow the tool to create a temporary layer, and don't keep any FID or ID column from the overlay layer; the output needs to have only the fid, left, top, right, and bottom fields from the grid layer (anything after that won't hurt, but better to avoid possible confusion). Save that layer as a CSV file named for it's corresponding block ("Block_0004_tile_list.csv" or something like that). You don't need to save any geometry. Check that file to make sure it has at least the five fields above (fid, left, top, right, and bottom _in that order).
    - _TODO maybe: When there are overlapping point clouds, consider cropping each one closer to its center. Presumably the outer points in each cloud are the least accurate._
- Create two empty directory called "clipped" and "cropped".
- Now you should have in your root directory:
  - Three subdirectories:
    - split_mask (full of small .gpkg files)
    - clipped (empty)
    - cropped (empty)
  - One or more CSV files with lists of tiles and their bounds&mdash;one for each point cloud.
  - Your original point cloud file(s) (.las or .laz)
  
On to the next step.

### Create the script to process the files.
We're doing something weird; using Python to write a Bash script. I know, I know, we could just call PDAL directly from Python. The advantage of this process is that the Bash script is editable, which makes it easier to multithread it, stop and restart it, and otherwise troubleshoot in mid-stream. If you don't like it, do please create a better system!

- In a Unix terminal with PDAL installed (lots of instructions on the Net to do this) navigate to the directory where your prepared files are.
- Invoke the script in this very repo using ```python create_split_merge_pdal_crop_and_clip_command.py lasfile.laz csvfile.csv script_for_this_block.sh```. That'll create a Bash script for you (you can read it if you're curious).
- Make the script executable with ```sudo chmod +x script_for_this_block.sh```.
- Run it with ```./script_for_this_block.sh```. If all goes well, that'll start by creating a new version of the original point cloud file that's been filtered for outliers, classified using the SMRF filter, and all points that those algorithms don't think are ground are tossed out. Then it'll clip that into little bitty peices (in the clipped directory) and crop them using the mask files (into the cropped directory).
- When it finishes, select _all of the files in the cropped directory_. In your terminal, type ```pdal merge ```, drop the huge file list in, and finish the incantation with ```mypointcloud_clipped_and_re-merged.laz``` or whatever you want to call it.
- You probably want to rasterize it later, there's a PDAL incantation for that in the notes section.


## Notes

- Regenerated the DSM directly from PDAL. This could be useful because it should be possible to combine all of the point clouds into one giant point cloud, which will get rid of any seams along merge cutlines.

- Used QGIS to clip the raster (from a ground polygon, which was in turn generated by subtracting the buildings&trees from the block boundary).

- QGIS fill nodata (works where GRASS seems to choke). Used a 50 pixel search radius. Seems to make a rounded bump where the buildings were, but certainly less of a bump than in the original. Might want to see if it can be tweaked to not round (just slap a plane across the hole).

- [Very useful list of tools](https://www.usna.edu/Users/oceano/pguth/md_help/html/dtm_creation.htm) from the United States Naval Academy including a [discussion of the PDAL tools](https://www.usna.edu/Users/oceano/pguth/md_help/html/pdal.htm)

- Apparently the [SAGA GIS close gaps tool](https://gisgeography.com/how-to-fill-nodata-raster-data/) is quick and dirty. Might be good if it doesn't try to make a nice round top!

- Nice to know [I'm not the only person with this problem](https://www.mdpi.com/2072-4292/11/1/24/htm). There are some academics who make it clear that big holes in DEMs are a common problem.

- GDAL clip raster command:
```
gdalwarp -of GTiff -cutline path/to/cutfile.gpkg -cl cutfile -crop_to_cutline path/to/infile.tif path/to/outfile.tif
```

- PDAL translate filter command example
```
pdal translate odm_georeferenced_model_block_0005.laz -o block_0005_denoised_ground_only.laz outlier smrf range --filters.outlier.method="statistical" --filters.outlier.mean_k=8 --filters.outlier.multiplier=3.0 --filters.smrf.ignore="Classification[7:7]" --filters.range.limits="Classification[2:2]" --writers.las.compression=true --verbose 4
```

- PDAL crop command
```
pdal translate $infile -o "cropped/$square.laz" crop --filters.crop.bounds="([$xmin,$xmax],[$ymin,$ymax])" --writers.las.compression=true --verbose 4
```

- PDAL classify command
```
pdal translate $clippedfile -o "clipped/$square.laz" overlay --filters.overlay.datasource='/home/ivan/Documents/Maps/River_mapping/point_clouds/split_mask/fid_1401.gpkg' --filters.overlay.column="CLS" --filters.overlay.dimension="Classification"
```
- PDAL pre-classification (works on large point cloud)
```
pdal translate odm_georeferenced_model_block_0004.laz -o block_0004_pre-classified.laz outlier smrf --filters.outlier.method="statistical" --filters.outlier.mean_k=8 --filters.outlier.multiplier=3.0 --filters.smrf.ignore="Classification[7:7]" --writers.las.compression=true --verbose 4
```

-PDAL classify and clip
```
pdal translate $clippedfile -o "clipped/$square.laz" overlay range --filters.overlay.datasource='/home/ivan/Documents/Maps/River_mapping/point_clouds/split_mask/fid_1401.gpkg' --filters.overlay.column="CLS" --filters.overlay.dimension="Classification" --filters.range.limits="Classification[0:5]" --verbose 4
```

# Overall Steps
- Take the point cloud for each individual block from the photogrammetry software and classify it using the PDAL Outlier and Simple Morphological Filter tools.
  - Settings for the Outlier filter: ```--filters.outlier.method="statistical" --filters.outlier.mean_k=8 --filters.outlier.multiplier=3.0``` 
- Check the resulting point cloud in CloudCompare to see if the classification makes sense (mostly to make sure that anything that is ground doesn't get classified as non-ground).
- Filter out all points not classified as ground (only keep points classified by the SMRF as 2&mdash;ground). 
- Clip the point cloud with the PDAL Overlay filter using the OSM buildings with a 1.2m buffer. This step appears necessary because many areas with low, tightly-packed buildings fool the SMRF filter into thinking the rooftops are the ground.
- Clip off the edges. Where the point clouds overlap, choose a cutline for each point cloud that overlaps a few meters with the neighboring one.
- Merge the point clouds with PDAL merge.
- Rasterize the point clouds to a 12cm GeoTIFF file.
- Import the resulting GeoTiff file into QGIS. It's more holes than points, because outside of the actual river valley there's more rooftop area than ground area visible from the sky. At the edges of the holes, there's often a raised lip due to a few points from the buildings that snuck in (whether they were classified by the SMRF or masked out). Clip those in the raster so that the ground edges don't have raised borders.
- Use the QGIS "Fill nodata" tool to place a naive slab of interpolated pixels over the top of the holes.
  - The GDAL command for this is ```gdal_fillnodata.py -md 100 -b 1 -of GTiff infile.tif outfile.tif``` where ```-md``` is the number of pixels to reach out.