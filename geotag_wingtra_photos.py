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
    
def images(indir):
    """Get a list of images that hopefully corresponds to the locations in the flight log"""
    image_files = scandir(indir)
    
    
if __name__ == "__main__":
    """Expects a json file with flight data and a directory of images"""
    flight_log_file = sys.argv[1]
    image_directory = sys.argv[2]
    (locations,geotxt) = extract_locations(flight_log_file)
    locations.sort(key = lambda x: int(x[0])) #sort by sequence, maybe should be timestamp
    image_files = scandir(image_directory)
    image_files.sort() #alphabetize the fuckers

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
        writer.writerow(['file','sequence','lat','lon','elevation','timestamp',
                         'hAccuracy','vAccuracy','pitch','roll','yaw','version'])
        writer.writerows(merged_locations)
        
    with open(geotxt, 'w') as geotxt_file:
        writer = csv.writer(geotxt_file, delimiter = ' ')
        writer.writerow(['EPSG:4326'])
        writer.writerows(merged_geo)



    
