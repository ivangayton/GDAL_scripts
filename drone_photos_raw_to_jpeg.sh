#!/bin/bash

# Use RawTherapee-cli to autolevel the photos and cut them down to half size
# Need a .pp3 file that specifies autolevel and scaling

rawtherapee-cli -p autolevel_and_halfsize.pp3 -o output/dir/ -c raw/images/dir/

# Use exiftool to copy over all of the metadata tags (drone photos have more
# than EXIF, they also have XMP and some other shit, need to copy all.
# Most of the exif viewers/libraries struggle with this, exiftool rocks it.

sd=<source/dir>; td=<target/dir>; for f in $sd/*; do fn="$(b=${f##*/}; echo "${b%.*}")"; exiftool -TagsFromFile $sd/$fn.DNG "-all:all>all:all" $td/$fn.jpg; rm $td/$fn.jpg_original; done;


