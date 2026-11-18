#! /usr/bin/python3
"""
"""

import sys, os
import csv

def scandir(dir):
    """
    Walk recursively through a directory and return a list 
    of all files in it and its subdirectories.
    """
    filelist = []
    for path, dirs, files in os.walk(dir):
        for f in files:
            filelist.append(os.path.join(path, f))
    return filelist

if __name__ == "__main__":
    """Expects a directory as the first argument and a CSV as the second"""
    files = scandir(sys.argv[1])
    tasks = list(open(sys.argv[2]))
    for task in tasks:
        line = task.split(',')
        print(f'{line[0]} - {line[2]}')
