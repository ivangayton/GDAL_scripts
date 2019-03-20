# Using OpenDroneMap on a Digital Ocean cloud machine from a low-bandwidth location

ODM can't always be effectively set up locally, so a cloud machine can sometimes be the answer. Bandwidth is a problem. It can't be solved, but the following method does a reasonable job of reducing the bandwidth needed to process image datasets on the cloud from African locations.

# Steps - Overview
- Create a Digital Ocean droplet of minimal size/cost
  - Should be an Ubuntu 16.04 instance to ensure dependency compatibility
- Download and install ODM on it from the ODM Github (regular, not WebODM)
- Meanwhile (you can do this while ODM installs), push your images onto the server
  - This will take some bandwidth. No way around that.
- Shut down and resize your machine to an appropriately monstrous number of CPUs and amount of memory. Restart, and get to work quickly so as not to waste expensive big-droplet time.
- Launch the ODM instance via ssh using nohup (so that if you're cut off, processing will continue)
```
nohup python run.py -i /path/to/image/folder project_name
```

- Follow the progress using tail (so that you'll know when it's done)
```
tail -f nohup.out
```

- Keep an eye on htop (to get a sense of the resource usage so that in future you can only spin up a machine as large as necessary)
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

