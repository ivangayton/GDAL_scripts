# Using OpenDroneMap on a Digital Ocean cloud machine from a low-bandwidth location

ODM can't always be effectively set up locally, so a cloud machine can sometimes be the answer. Bandwidth is a problem. It can't be solved, but the following method does a reasonable job of reducing the bandwidth needed to process image datasets on the cloud from African locations.

# Steps - Overview
- Create a Digital Ocean droplet with at least 4GB of RAM (less than that and the install will fail&mdash;you can downsize it between runs to the second-cheapest droplet)
  - Should be an Ubuntu 16.04 instance to ensure dependency compatibility
- Download and install ODM on it from the ODM Github (regular, not WebODM)

```
git pull https://github.com/OpenDroneMap/ODM.git
cd ODM
bash configure.sh install
```

- (From [the ODM github](https://github.com/OpenDroneMap/ODM)) There are some environmental variables that need to be set. Open the ~/.bashrc file on your machine and add the following 3 lines at the end. The file can be opened with ```nano ~/.bashrc```. Be sure to replace the "/your/path/" with the correct path to the location where you extracted OpenDroneMap:

```
export PYTHONPATH=$PYTHONPATH:/your/path/OpenDroneMap/SuperBuild/install/lib/python2.7/dist-packages
export PYTHONPATH=$PYTHONPATH:/your/path/OpenDroneMap/SuperBuild/src/opensfm
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/your/path/OpenDroneMap/SuperBuild/install/lib
```

- Now you'll need a hard drive (Volume in Digital Ocean jargon) big enough to manage your project. Rule of thumb seems to be 10 times the size of your raw image set. Set up the volume, attach it to your droplet, and configure its mount point (in this example setting it to /mnt/odmdata/).  
- Now push your images onto the server
  - This will take some bandwidth. No way around that.
    - That's not quite true (that there's no way around it). If you compress the images into  JPEG with YCbCr instead of RGB, this retains essentially all of the feature detail in the luminance channel (Y) and compresses the chrominance channels (Cb and Cr) which shouldn't reall affect the quality of the ODM output (ODM only uses a single band to generate the point cloud anyway; in fact it's possible that it will increase the quality of the point cloud matching because the luminance channel will probably have more contrast than any of the RGB channels) and will get you a substantial reduction in file size. But honestly, you only want to mess with this if you're desperate to save bandwidth.

- Folder structure should be:
  - One project folder on your second drive (volume). This is what goes in the project path line of the settings.yaml file. It contains the gcp_list.txt file, the image_groups.txt file, and the images folder. In this example I'm using ```/mnt/odmdata/myproject/```
  - ```/mnt/odmdata/myproject/images/``` This contains all of the images. If you set it up like this, the images don't get re-copied because they're already in the directory that ODM wants them in. 
- If you've got images with GPS info on them (as from an Ebee), use exiftool to massage the GPS information ```exiftool "-GPSDOP<GPSZAccuracy" .```
  - This takes the Z error estimate that the ebee sets and copies that tag to the DOP tag, where OpenDroneMap will read it and use it to constrain the SfM modeling process (i.e. : optimize this model, but don’t move the cameras further than the dilution off precision estimate, instead modify other aspects of camera pose and lens parameters).
  - Yes, you'll probably have to install exiftool. The command might be ```sudo apt install libimage-exiftool-perl```.

- Modify settings.yaml to specify the project folder i.e. ```/mnt/odmdata/myproject/```. Make sure the images are in the correct spot, i.e. ```/mnt/odmdata/myproject/images``` and the other ancillary files (gcp_list.txt and image_groups.txt) are in the root folder ```/mnt/odmdata/myproject/```

- Shut down and resize your machine to an appropriately monstrous number of CPUs and amount of memory. Restart, and get to work quickly so as not to waste expensive big-droplet time.
- Launch the ODM process via ssh using nohup (so that if you're cut off, processing will continue)
  - Alternately you can use GNU screen to launch the process from a screen session which won't stop if your connection is interrupted; launch ```screen```, and use ```<ctrl> a <ctrl> d``` to detach, ```screen -r``` to re-attach.

  - Note: as of 2020-03 the normal incantation ```nohup python run.py -i /path/to/image/folder project_name``` seems _not_ to work; the ```-i``` or ```--image``` parameter causes an error. So we drop the -i parameter, and rely on the project directory line in the settings.yaml file to direct ODM to the right place. Now using (including a split-merge):

```
nohup python run.py projectname --split 1 --split-overlap 0 --ignore-gsd --depthmap-resolution 1000 --orthophoto-resolution 3 --dem-resolution 12 --pc-las --dsm
```

  - Note that this assumes you have an image_groups.txt file. If not, this ```-split-overlap 0``` will probably fuck things up, and the ```--split 1``` is literally a random number that will be ignored after the image_groups.txt file is loaded (I think it normally controls how many groups it splits a set of images into, but in our case we're assuming the images are already grouped sensibly).
  - Speaking of grouping images sensibly, if you have the images in separate folders for individual AOI blocks or flights (which you will if your flight management was organized), you can create an image_groups.txt file with the incantations ```for i in *; do cd $i; for j in *; do echo "$j $i" >> ../$i.txt; done; cd ../; done;``` and ```for i in myDirectory/*.txt; do cat $i >> image_groups.txt; done;```. Then move all of the image files into a single directory called images in the project root dir.

- Follow the progress using tail (so that you'll know when it's done)

```
tail -f nohup.out
```

- You may want to keep an eye on htop (to get a sense of the resource usage so that in future you can only spin up a machine as large as necessary)
- As soon as processing is done, shut down the machine and resize it back down to the inexpensive minimum capacity.
- Start the machine back up, and log in via ssh.
- Compress the orthophoto using GDAL. Don't add overviews, do that on your local machine to avoid making the file bigger before downloading it.
```
gdal_translate -co COMPRESS=JPEG -co PHOTOMETRIC=YCBCR -co TILED=YES -b 1 -b 2 -b 3 -mask 4 --config GDAL_TIFF_INTERNAL_MASK YES /path/to/original/filename.extension /path/to/output.tif
```

- Archive the odm_texturing folder using tar
```
tar -zcvf archivename /path/to/folder
```
