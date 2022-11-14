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
            filelist.append(os.path.join(path, f))
    return filelist
    
def extract_locations(infile):
    """Return a list of locations and timestamps"""
    contents = json.load(open(infile))
    track = contents['flights'][0]['geotag']
    csv = []
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

        csv.append([sequence,lat,lon,ele,timestamp,hacc,
                    vacc,pitch,roll,yaw,version])
    return csv       
    
def create_geotag_list(indir):
    """Create a CSV file with a list of photos and their lat & long"""
    outfile = indir + '.csv'
    image_files = scandir(indir)
    writer = csv.writer(open(outfile, 'w'), delimiter = ',')
    writer.writerow(['file', 'path', 'directory', 'lat', 'lon'])
    
    for image_file in image_files:
        (image_path, image_ext) = os.path.splitext(image_file)
        image_filename = os.path.basename(image_file)
        image_dirname = os.path.dirname(image_file)
        if(image_ext == '.JPG' or image_ext == '.jpg'):
            crds = extract_location(image_file)
            if(crds):
                writer.writerow([image_filename, image_file, image_dirname,
                                 crds[0], crds[1]]) 
    
    
if __name__ == "__main__":
    """Expects a json file with flight data and a directory of images"""
    flight_log_file = sys.argv[1]
    image_directory = sys.argv[2]
    locations = extract_locations(flight_log_file)
    outcsv_file = os.path.splitext(flight_log_file)[0] + '.csv'
    with open(outcsv_file, 'w') as outf:
        writer = csv.writer(outf)
        writer.writerow(['sequence','lat','lon','elevation','timestamp',
                         'hAccuracy','vAccuracy','pitch','roll','yaw','version'])
        writer.writerows(locations)


    
