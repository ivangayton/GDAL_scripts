# Using OpenDroneMap on a Digital Ocean cloud machine from a low-bandwidth location

ODM can't always be effectively set up locally, so a cloud machine can sometimes be the answer. Bandwidth is a problem. It can't be solved, but the following method does a reasonable job of reducing the bandwidth needed to process image datasets on the cloud from African locations.

# Steps - Overview
- Create a Digital Ocean droplet of minimal size/cost
  - Should be an Ubuntu 16.04 instance to ensure dependency compatibility
- Download and install ODM on it from the ODM Github (regular, not WebODM)
  - This requires upsizing the droplet to at least 4GB of RAM. Then pull from GitHub and perform the native install.
- Meanwhile (you can do this while ODM installs), push your images onto the server
  - This will take some bandwidth. No way around that.

-If you've got images with GPS info on them (as from an Ebee), use exiftool to massage the GPS information ```exiftool "-GPSDOP<GPSZAccuracy" .```
  - This takes the Z error estimate that the ebee sets and copies that tag to the DOP tag, where OpenDroneMap will read it and use it to constrain the SfM modeling process (i.e. : optimize this model, but don’t move the cameras further than the dilution off precision estimate, instead modify other aspects of camera pose and lens parameters).

- Modify settings.yaml to specify the project folder i.e. ```/mnt/odmdrive/myproject/```. Make sure the images are in the correct spot, i.e. ```/mnt/odmdrive/myproject/images``` and the other ancillary files (gcp_list.txt and image_groups.txt) are in the root folder.

- Shut down and resize your machine to an appropriately monstrous number of CPUs and amount of memory. Restart, and get to work quickly so as not to waste expensive big-droplet time.
- Launch the ODM process via ssh using nohup (so that if you're cut off, processing will continue)
  - Alternately you can use GNU screen to launch the process from a screen session which won't stop if your connection is interrupted; launch ```screen```, and use ```<ctrl> a <ctrl> d``` to detach, ```screen -r``` to re-attach.

  - Note: as of 2020-03 the normal incantation ```nohup python run.py -i /path/to/image/folder project_name``` seems _not_ to work; the ```-i``` or ```--image``` parameter causes an error. Now using (including a split-merge):

```nohup python run.py projectname --split 1 --split-overlap 0 --ignore-gsd --depthmap-resolution 1000 --orthophoto-resolution 3 --dem-resolution 12 --pc-las --dsm```

- Follow the progress using tail (so that you'll know when it's done)
```
tail -f nohup.out
```

- You may want to keep an eye on htop (to get a sense of the resource usage so that in future you can only spin up a machine as large as necessary)
- As soon as processing is done, shut down the machine and resize it back down to the original, inexpensive minimum.
- Start the machine back up, and log in via ssh.
- Compress the orthophoto using GDAL. Don't add overviews, do that on your local machine to avoid making the file bigger before downloading it.
```
gdal_translate -co COMPRESS=JPEG -co PHOTOMETRIC=YCBCR -co TILED=YES -b 1 -b 2 -b 3 -mask 4 --config GDAL_TIFF_INTERNAL_MASK YES /path/to/original/filename.extension /path/to/output.tif
```

- Archive the odm_texturing folder using tar
```
tar -zcvf archivename /path/to/folder
```
