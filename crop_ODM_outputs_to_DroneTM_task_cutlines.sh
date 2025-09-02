#!/bin/bash

# Set up a text file with the names of the tasks, which hopefully correspond reasonably closely to the names of the image files

# Useful rename command:
# for f in *; do mv "$f" "$(echo "$f" | sed s/THING_/THING_0/)"; done;

while read -r line; do gdalwarp -cutline task_bounds/$line.gpkg original/$line-backup.tif cropped/$line-cropped.tif; done < orthos.txt

# Should generate the command
# gdalwarp -cutline task_bounds/TASK_ID.gpkg original/TASK_ID.tif cropped/TASK_ID-cropped.tif


wait

# Add overviews
for i in cropped/*.tif; do
    echo $i
    gdaladdo -r average $i 2 4 8 16 32 64 128 256 512 1024 &
done



