#! /usr/bin/python3

import sys, os
import csv

def crt_outfl(infile, extension):
    try:
        infile_name = infile.split('.')[0]
        infile_extension = infile.split('.')[-1]
    except:
        print("check input file")
        sys.exit()
    outfile = infile_name + extension
    return outfile

def clean(infile):
    data = list(csv.reader(open(infile), delimiter = ','))
    writer = csv.writer(open(crt_outfl
                             (infile, '_cleaned.csv'), 'w'), delimiter = ',')
    header = [text.lower() for text in data.pop(0)]
    header.append('errors')
    writer.writerow(header)

    for item in data:
        fields = [text.strip() for text in item]
        fields = [text.replace('\n', ' ') for text in fields]

        # Add specific cleaning functions here!
        
        writer.writerow(fields)

if __name__ == "__main__":
    clean(sys.argv[1])
