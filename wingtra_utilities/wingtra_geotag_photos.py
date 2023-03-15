#! /usr/bin/python3
"""

"""

import sys, os
import shutil
import csv
import json

def scandir(dir):
    """Walk recursively through a directory and 
    return a list of all files in it"""
    filelist = []
    for path, dirs, files in os.walk(dir):
        for f in files:
            filelist.append(f)
    return filelist

def is_wingtra_dir(indir):
    """Checks if a directory has an IMAGES subdirectory
    with at least one JPG image file in it,
    and a DATA subdirectory containing at least one json file
    which would be consistent with a Wingtra data directory.
    """
    
    dp = os.path.join(indir, 'DATA')
    ip = os.path.join(indir, 'IMAGES')
    if os.path.exists(dp) and os.path.exists(ip):
        all_data_files = os.listdir(dp)
        flight_log_file = [f for f in all_data_files if
                           os.path.splitext(f)[1].lower() == '.json']
        all_image_files = os.listdir(ip)
        imagefilelist = [f for f in all_image_files if
                         os.path.splitext(f)[1].lower() == '.jpg']
        if imagefilelist and flight_log_file:
            return True
        else:
            return False
    else:
        return False
        
def get_wingtra_dirs(indir):
    """Find directories containing DATA and IMAGES subdirs"""
    dirlist = []
    for path, dirs, files in os.walk(indir):
        for d in dirs:
            dirlist.append(os.path.join(path, d))
    wingtra_dirs = []
    for d in dirlist:
        if is_wingtra_dir(d):
            wingtra_dirs.append(d)
    return wingtra_dirs
    
def extract_locations(infile):
    """Return a list of locations and timestamps"""
    contents = json.load(open(infile))
    track = contents['flights'][0]['geotag']
    csv = []
    geotxt = []
    for point in track:
        coord = point['coordinate']
        lat = coord[0]
        lon = coord[1]
        ele = coord[2]
        timestamp = point['timestamp']
        hacc = point['hAccuracy']
        vacc = point['vAccuracy']
        pitch = point['pitch']
        roll = point['roll']
        yaw = point['yaw']
        sequence = point['sequence']
        version = point['version']
        
        csv.append([sequence,lat,lon,ele,timestamp,
                    hacc,vacc,pitch,roll,yaw,version])
        # for now ignoring the pitch, roll, and yaw until
        # I understand how they work
        geotxt.append([lon,lat,ele,0,0,0,hacc,vacc])
        
    return (csv,geotxt)       

def geotag(indir):
    """
    Side effects: writes outfiles

    Join the images and locations.
    Create a csv file useful for viewing in QGIS.
    Create a txt file in the format of an ODM geo.txt
    (though not actually named geo.txt for now).
    """
    # Grab the json file in the DATA dir
    # This is illegible and fragile, whatever, suck it up
    data_dir = os.path.join(indir, 'DATA')
    data_files = os.listdir(data_dir)
    flight_log_file = ''
    try:
        flight_log_file = os.path.join(data_dir,
                                 [x for x in data_files if
                                  os.path.splitext(x)[1] == '.json']
                                 [0])
    except Exception as e:
        print(e)
        print(f'\nYour directory structure in {indir} is probably '
              f'not as expected')
                
    # Grab the images directory
    image_directory = os.path.join(indir, 'IMAGES')
    (locations,geotxt) = extract_locations(flight_log_file)

    #sort by sequence, probably should be timestamp
    locations.sort(key = lambda x: int(x[0]))
    all_files = os.listdir(image_directory)
    image_files = [x for x in all_files if
                   os.path.splitext(x)[1].lower() == '.jpg']

    #alphabetize the fuckers, hope for the best
    image_files.sort() 

    # Join the photos and locations with zip
    # There is a weird and scary inconsistency in the image file
    # names; they seem to start at 00002, while the locations
    # have a sequence attribute that starts at 1. Assuming
    # it is consistent in Wingtra data and hoping for the best.
    zipped = zip(image_files, locations)
    merged_locations = []
    for item in zipped:
        newloc = []
        newloc.append(item[0])
        newloc.extend(item[1])
        merged_locations.append(newloc)

    zippedgeo = zip(image_files, geotxt)
    merged_geo = []
    for item in zippedgeo:
        newloc = []
        newloc.append(item[0])
        newloc.extend(item[1])
        merged_geo.append(newloc)
    
    outcsv_file = os.path.splitext(flight_log_file)[0] + '.csv'
    geotxt = os.path.splitext(flight_log_file)[0] + '.txt'
    with open(outcsv_file, 'w') as outf:
        writer = csv.writer(outf)
        writer.writerow(['file','sequence','lat','lon',
                         'elevation','timestamp',
                         'hAccuracy','vAccuracy','pitch',
                         'roll','yaw','version'])
        writer.writerows(merged_locations)
        
    with open(geotxt, 'w') as geotxt_file:
        writer = csv.writer(geotxt_file, delimiter = ' ')
        writer.writerow(['EPSG:4326'])
        writer.writerows(merged_geo)

    geo_txt_in_images_dir = os.path.join(image_directory, 'geo.txt')
    shutil.copy(geotxt, geo_txt_in_images_dir)    

    print(f'Wrote \n- {outcsv_file},\n- {geotxt}, '
          f'and \n- {geo_txt_in_images_dir}\n')
    return 0
    
if __name__ == "__main__":
    """Expects a directory with three subdirectories. The DATA
    directory should contain a JSON file with the locations of the
    photos taken by the Wingtra (this seems to be Wingtra's default
    format), and the Images directory a bunch of sequentially named
    jpg images. Like so:

    -MyFlight02
      -DATA
        MyFlight02.json
        MyFlight02 WingtraOne.sbf
      -FLIGHT RECORD
      -IMAGES
        MyFlight02_01_00002.JPG
        MyFlight02_01_00003.JPG
        ...

    If the directory does not have that structure, it looks for
    subdirectories that do and, if it finds them, processes them
    individually.

    So far it looks like the locations and photos sort correctly 
    with naive alphabetization, so when we zip them to join the 
    coordinates to the appropriate images it seems to work, though 
    that's a dangerous assumption (risking it for now). 

    """
    indir = sys.argv[1]

    # Check if the indir is a Wingtra directory
    if is_wingtra_dir(indir):
        geotag(indir)
    else:
        wingtra_dirs = get_wingtra_dirs(indir)
        for d in wingtra_dirs:
            geotag(d)
