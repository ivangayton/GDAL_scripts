# Unzipping a bunch of archives from S3, mostly backups from ODM

Make sure big archives that might trigger zipbomb detection can be extracted (ODM backups seem to trip the zipbomb detection threshold
```
export UNZIP_DISABLE_ZIPBOMB_DETECTION=TRUE
```

Traverse a pile of zipfiles, check if they've already been extracted into the target directory, if not unzip
```
for f in *.zip; do if [ ! -d /run/media/ivan/bd021b2f-439b-4218-a210-eae706296cb9/Unzipped_Freetown_data_from_S3/${f%.*} ]; then mkdir /run/media/ivan/bd021b2f-439b-4218-a210-eae706296cb9/Unzipped_Freetown_data_from_S3/${f%.*} && unzip $f -d /run/media/ivan/bd021b2f-439b-4218-a210-eae706296cb9/Unzipped_Freetown_data_from_S3/${f%.*}; else echo "not overwriting ${f%.*}"; fi; done;
```