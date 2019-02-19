# -*- coding: utf-8 -*-

import argparse
import glob
import os
from PIL import Image
from pprint import pprint
import sys

import lib.io_utils as io

# input
parser = argparse.ArgumentParser()
parser.add_argument('-in', dest="IMAGE_FILES", default="downloads/historic_thumbnails/*.jpg", help="Input file pattern")
parser.add_argument('-out', dest="OUTPUT_DIR", default="img/historic_thumbnails/", help="Directory to export files to")
parser.add_argument('-width', dest="THUMB_WIDTH", default=128, type=int, help="Thumb width")
parser.add_argument('-overwrite', dest="OVERWRITE", action="store_true", help="Overwrite existing images?")
a = parser.parse_args()

# Make sure output dirs exist
io.makeDirectories(a.OUTPUT_DIR)
filenames = glob.glob(a.IMAGE_FILES)
fileCount = len(filenames)

for i, fn in enumerate(filenames):
    basename = os.path.basename(fn)
    outFilename = a.OUTPUT_DIR + basename

    if not os.path.isfile(outFilename) or a.OVERWRITE:
        im = Image.open(fn)
        im.thumbnail((a.THUMB_WIDTH, a.THUMB_WIDTH))
        im.save(outFilename)

    sys.stdout.write('\r')
    sys.stdout.write("%s%%" % round(1.0*(i+1)/fileCount*100,2))
    sys.stdout.flush()
