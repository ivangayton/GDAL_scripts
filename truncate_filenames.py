#!/bin/python3
import sys, os

def rename_files_and_geotxt(indir, nukewords):
    filelist = os.listdir(indir)
    imagefiles = [x for x in filelist if
                  os.path.splitext(x)[1].lower() == '.jpg']
    geotxtfilename = os.path.join(indir, 'geo.txt')
    newfilelist = []
    for imagefile in imagefiles:
        old = os.path.join(indir, imagefile)
        newimagefile = imagefile
        for nukeword in nukewords:
            newimagefile = newimagefile.replace(nukeword, '')
        new = os.path.join(indir, newimagefile)

        os.rename(old, new)

    newlines = []
    with open(geotxtfilename) as gt:
        lines = gt.readlines()
        for line in lines:
            newline = line
            for nukeword in nukewords:
                newline = newline.replace(nukeword, '')
            newlines.append(newline)
            

    os.rename(geotxtfilename, os.path.join(indir, 'geo.txtBAK'))
    with open(os.path.join(indir, 'geo.txt'), 'w') as tgt:
        tgt.writelines(newlines)
            

        
    
if __name__ == '__main__':
    """ """
    indir = sys.argv[1]
    nukewords = sys.argv[2:]
    print(f"Undertaking to remove {', '.join(nukewords)} in {indir}")
    rename_files_and_geotxt(indir, nukewords)
    
    
    
    
