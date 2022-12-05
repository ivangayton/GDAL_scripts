#! /usr/bin/python3
"""

"""

import sys, os
import csv
import json

def scandir(dir):
    """Walk recursively through a directory and return a list of all files in it"""
    filelist = []
    for path, dirs, files in os.walk(dir):
        for f in files:
            filelist.append(f)
    return filelist
    
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

def geotag(flight_log_file, image_directory):
    """
    Side effects: writes outfiles

    Join the images and locations.
    Create a csv file useful for viewing in QGIS.
    Create a txt file in the format of an ODM geo.txt
    (though not actually named geo.txt for now).
    """
    (locations,geotxt) = extract_locations(flight_log_file)

    #sort by sequence, probably should be timestamp
    locations.sort(key = lambda x: int(x[0]))
    image_files = scandir(image_directory)

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

    So far it looks like the locations and photos sort correctly 
    with naive alphabetization, so when we zip them to join the 
    coordinates to the appropriate images it seems to work, though 
    that's a dangerous assumption (risking it for now). 

    """
    indir = sys.argv[1]

    # Grab the json file in the DATA dir
    # This is illegible and fragile, whatever, suck it up
    data_dir = os.path.join(indir, 'DATA')
    data_files = scandir(data_dir)
    flight_log_file = ''
    try:
        flight_log_file = os.path.join(data_dir,
                                 [x for x in data_files if
                                  os.path.splitext(x)[1] == '.json']
                                 [0])
    except exception as e:
        print(e)
        print('\nYour directory structure is probably not as expected')
        
    # Grab the images directory
    image_directory = os.path.join(indir, 'IMAGES')

    result = geotag(flight_log_file, image_directory)

    
